"""Main entry point."""

import argparse
import socket
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from .downloader import DownloaderConfig
from .queue_manager import DownloadQueue

console = Console()


def load_links_from_file(filepath: str) -> list[str]:
    path = Path(filepath)
    if not path.exists():
        console.print(f"[red]File not found: '{filepath}'[/]")
        sys.exit(1)

    lines = path.read_text().strip().splitlines()
    links = [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]

    if not links:
        console.print(f"[yellow]No links in '{filepath}'[/]")
        sys.exit(0)

    return links


def detect_system_proxy() -> str:
    common_proxies = [
        ("socks5://127.0.0.1", 1080),
        ("socks5://127.0.0.1", 10808),
        ("http://127.0.0.1", 7890),
        ("http://127.0.0.1", 8080),
        ("http://127.0.0.1", 10809),
    ]

    for proxy_base, port in common_proxies:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            if result == 0:
                proxy = f"{proxy_base}:{port}"
                console.print(f"  🔍 [green]Found proxy:[/] {proxy}")
                return proxy
        except Exception:
            continue

    return ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fast YouTube video downloader with queue support",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-f", "--file", help="Text file with YouTube links")
    source.add_argument("-u", "--urls", nargs="+", help="YouTube URLs")

    parser.add_argument("-o", "--output", default="./downloads", help="Output dir")
    parser.add_argument(
        "-j", "--fragments", type=int, default=4, help="Concurrent fragments"
    )
    parser.add_argument("--proxy", default=None, help="Proxy URL")
    parser.add_argument("--no-proxy", action="store_true", help="Disable proxy")
    parser.add_argument("--retries", type=int, default=5, help="Max retries")

    return parser.parse_args()


def main():
    console.print(
        Panel(
            "[bold cyan]🎬 YouTube Video Downloader[/]\n"
            "[dim]720p · No ffmpeg needed · Auto proxy[/]",
            style="blue",
        )
    )

    args = parse_args()

    if args.file:
        links = load_links_from_file(args.file)
        console.print(
            f"📄 Loaded [bold]{len(links)}[/] link(s) from [cyan]{args.file}[/]"
        )
    else:
        links = args.urls
        console.print(f"🔗 [bold]{len(links)}[/] link(s) from command line")

    if args.no_proxy:
        proxy = ""
        console.print("🌐 Proxy: [yellow]Disabled[/]")
    elif args.proxy:
        proxy = args.proxy
        console.print(f"🌐 Proxy: [cyan]{proxy}[/]")
    else:
        console.print("🌐 Proxy: [dim]Auto-detecting...[/]")
        proxy = detect_system_proxy()
        if not proxy:
            console.print("  [yellow]⚠ No proxy found[/]")

    config = DownloaderConfig(
        output_dir=args.output,
        max_retries=args.retries,
        concurrent_fragments=args.fragments,
        proxy=proxy,
    )

    console.print(f"📁 Output: [cyan]{config.output_dir}[/]")
    console.print(f"🎥 Quality: [cyan]720p (no ffmpeg needed)[/]")

    queue = DownloadQueue(config)
    queue.add_many(links)
    queue.process()


if __name__ == "__main__":
    main()
