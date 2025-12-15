"""download_csv.py

Small utility to download a CSV from a URL or copy a local workspace CSV
to a destination path. Designed to be simple and work on Windows PowerShell.

Usage examples:
  python download_csv.py --url https://example.com/data.csv --out data.csv
  python download_csv.py --src-file nikhil_kamath_50_videos.csv --out copy.csv

"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    import requests
except Exception:  # pragma: no cover - friendly error
    requests = None


def download_url(url: str, out_path: Path) -> None:
    if requests is None:
        raise RuntimeError("The 'requests' package is required. Install with: pip install requests")
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def copy_local(src: Path, out_path: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out_path)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download or copy a CSV into the workspace")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", help="HTTP(s) URL to download the CSV from")
    g.add_argument("--src-file", help="Path to a local file in the workspace to copy")
    p.add_argument("--out", "-o", default="downloaded.csv", help="Output filename")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_path = Path(args.out)
    try:
        if args.url:
            print(f"Downloading {args.url} -> {out_path}")
            download_url(args.url, out_path)
        else:
            src = Path(args.src_file)
            print(f"Copying {src} -> {out_path}")
            copy_local(src, out_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    print(f"Saved to {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
