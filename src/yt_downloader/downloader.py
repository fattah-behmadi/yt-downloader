"""Core download logic using yt-dlp."""

import os
from dataclasses import dataclass
from enum import Enum
from urllib.parse import parse_qs, urlparse, urlencode, urlunparse

import yt_dlp
from rich.console import Console

console = Console()


class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DownloadTask:
    url: str
    title: str = ""
    status: DownloadStatus = DownloadStatus.PENDING
    error: str = ""
    filename: str = ""
    progress: float = 0.0


@dataclass
class DownloaderConfig:
    output_dir: str = "./downloads"
    max_retries: int = 5
    concurrent_fragments: int = 4
    proxy: str = ""


def clean_url(url: str) -> tuple[str, bool]:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    has_video = "v" in params
    has_list = "list" in params

    if has_video and has_list:
        clean_params = {
            k: v[0] for k, v in params.items() if k not in ("list", "index")
        }
        new_query = urlencode(clean_params)
        cleaned = urlunparse(parsed._replace(query=new_query))
        return cleaned, False

    if has_list and not has_video:
        return url, True

    return url, False


class VideoDownloader:
    def __init__(self, config: DownloaderConfig | None = None):
        self.config = config or DownloaderConfig()
        os.makedirs(self.config.output_dir, exist_ok=True)

    def _get_base_opts(self) -> dict:
        opts = {
            "quiet": True,
            "no_warnings": True,
            "retries": self.config.max_retries,
            "fragment_retries": self.config.max_retries,
            "socket_timeout": 30,
            "extractor_retries": 5,
            "sleep_interval": 1,
            "max_sleep_interval": 5,
            "sleep_interval_requests": 1,
            "noplaylist": True,
            # ⬇️ FORCE: never merge, never need ffmpeg
            "format": "best[height<=720]/best",
            "prefer_free_formats": False,
            "postprocessors": [],
            "abort_on_error": False,
        }

        if self.config.proxy:
            opts["proxy"] = self.config.proxy

        return opts

    def _make_progress_hook(self, task: DownloadTask):
        def hook(d: dict):
            if d["status"] == "downloading":
                task.status = DownloadStatus.DOWNLOADING
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    task.progress = (downloaded / total) * 100
                speed = d.get("speed")
                speed_str = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "..."
                eta = d.get("eta", "?")
                console.print(
                    f"  ↓ [cyan]{task.progress:.1f}%[/] | "
                    f"Speed: [green]{speed_str}[/] | "
                    f"ETA: [yellow]{eta}s[/]",
                    end="\r",
                )
            elif d["status"] == "finished":
                task.filename = d.get("filename", "")
                console.print(f"\n  ✓ [green]Download complete![/]")

        return hook

    def extract_playlist(self, url: str) -> list[str]:
        opts = {
            **self._get_base_opts(),
            "extract_flat": True,
            "noplaylist": False,
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if info and info.get("_type") == "playlist":
                    entries = info.get("entries", [])
                    urls = []
                    for entry in entries:
                        if entry:
                            vid = entry.get("id") or entry.get("url", "")
                            if vid:
                                urls.append(f"https://www.youtube.com/watch?v={vid}")
                    return urls

            return [url]

        except Exception as e:
            console.print(f"  [red]Playlist extraction failed: {e}[/]")
            return []

    def get_video_info(self, url: str) -> dict | None:
        opts = {**self._get_base_opts(), "extract_flat": False}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            console.print(f"  [yellow]Info fetch failed: {e}[/]")
            return None

    def download(self, task: DownloadTask) -> DownloadTask:
        ydl_opts = {
            **self._get_base_opts(),
            "outtmpl": os.path.join(self.config.output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [self._make_progress_hook(task)],
            "concurrent_fragment_downloads": self.config.concurrent_fragments,
            "buffersize": 1024 * 64,
            "http_chunk_size": 1024 * 1024 * 10,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(task.url, download=True)
                task.title = info.get("title", "Unknown")
                task.status = DownloadStatus.COMPLETED
                task.progress = 100.0
        except Exception as e:
            task.status = DownloadStatus.FAILED
            task.error = str(e)

        return task
