"""Queue manager for processing download tasks sequentially."""

from collections import deque

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .downloader import (
    DownloadStatus,
    DownloadTask,
    DownloaderConfig,
    VideoDownloader,
    clean_url,
)

console = Console()


class DownloadQueue:
    def __init__(self, config: DownloaderConfig | None = None):
        self.queue: deque[DownloadTask] = deque()
        self.completed: list[DownloadTask] = []
        self.downloader = VideoDownloader(config)

    def add(self, url: str) -> None:
        """Add a URL. Auto-detects playlists vs single videos."""
        url = url.strip()
        if not url or url.startswith("#"):
            return

        cleaned, is_playlist = clean_url(url)

        if is_playlist:
            console.print(f"\n📋 [yellow]Playlist detected:[/] {url}")
            console.print("   Extracting videos...")

            video_urls = self.downloader.extract_playlist(cleaned)

            if video_urls:
                console.print(
                    f"   ✅ Found [bold]{len(video_urls)}[/] videos"
                )
                for v_url in video_urls:
                    self.queue.append(DownloadTask(url=v_url))
            else:
                console.print("   ❌ [red]Could not extract playlist[/]")
        else:
            if cleaned != url:
                console.print(
                    f"  🔗 [dim]Cleaned playlist params from URL[/]"
                )
            self.queue.append(DownloadTask(url=cleaned))

    def add_many(self, urls: list[str]) -> None:
        for url in urls:
            self.add(url)
        console.print(
            f"\n📊 Total videos in queue: [bold]{len(self.queue)}[/]"
        )

    def process(self) -> list[DownloadTask]:
        total = len(self.queue)
        if total == 0:
            console.print("[yellow]No videos in queue.[/]")
            return []

        console.print(
            Panel(
                f"[bold]Downloading {total} video(s)[/]",
                style="blue",
            )
        )

        index = 0
        while self.queue:
            index += 1
            task = self.queue.popleft()

            console.print(
                f"\n{'─' * 50}"
                f"\n[bold blue]▶ [{index}/{total}][/] {task.url}"
            )

            # Try to get info first
            info = self.downloader.get_video_info(task.url)
            if info:
                task.title = info.get("title", "Unknown")
                duration = info.get("duration", 0)
                if duration:
                    mins, secs = divmod(duration, 60)
                    hours, mins = divmod(mins, 60)
                    if hours:
                        dur_str = f"{hours}:{mins:02d}:{secs:02d}"
                    else:
                        dur_str = f"{mins}:{secs:02d}"
                else:
                    dur_str = "?"

                filesize = info.get("filesize_approx", 0)
                size_str = (
                    f"{filesize / 1024 / 1024:.0f} MB" if filesize else "?"
                )

                console.print(
                    f"  📹 [bold]{task.title}[/]"
                    f"\n  ⏱  {dur_str} | 📦 ~{size_str}"
                )

            # Download
            task = self.downloader.download(task)
            self.completed.append(task)

            if task.status == DownloadStatus.COMPLETED:
                console.print(f"  ✅ [green]Done![/]")
            else:
                console.print(f"  ❌ [red]Failed:[/] {task.error[:80]}")

        self._print_summary()
        return self.completed

    def _print_summary(self) -> None:
        console.print(f"\n{'═' * 50}")

        table = Table(title="📊 Download Summary", show_lines=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Title", style="white", max_width=45)
        table.add_column("Status", justify="center", width=8)

        succeeded = 0
        for i, task in enumerate(self.completed, 1):
            if task.status == DownloadStatus.COMPLETED:
                status = "[green]✅[/]"
                succeeded += 1
            else:
                status = "[red]❌[/]"

            title = task.title or task.url[:45]
            table.add_row(str(i), title, status)

        failed = len(self.completed) - succeeded

        console.print(table)
        console.print(
            f"\n[bold green]✅ {succeeded} succeeded[/]"
            + (f" | [bold red]❌ {failed} failed[/]" if failed else "")
        )
