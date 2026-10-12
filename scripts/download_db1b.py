"""Download the 13 quarterly U.S. DOT DB1B (Market) files used by this project.

The raw zips are 78-105 MB each (about 1.27 GB total) and are intentionally not
stored in the repository. This script fetches them into ``data/raw/db1b/``
(gitignored), verifies each file against the byte count recorded in
``data/flight/db1b_manifest.json``, and can optionally unzip them in place.

Downloads are resumable: if a partial file exists, only the remaining bytes are
requested, so the script is safe to stop and re-run. BTS can be slow and will
sometimes drop a connection; just run the script again to continue.

Usage:
    python scripts/download_db1b.py                 # fetch + verify, no unzip
    python scripts/download_db1b.py --unzip         # also unpack the CSVs
    python scripts/download_db1b.py --quarters 2024_2 2025_1
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "flight" / "db1b_manifest.json"
RAW_DIR = ROOT / "data" / "raw" / "db1b"

CHUNK = 1 << 20  # 1 MiB
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) db1b-fetch/1.0"


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:,.1f} {unit}"
        n /= 1024
    return f"{n:,.1f} TB"


def download(url: str, dest: Path, expected: int, retries: int = 4) -> None:
    """Resume-download ``url`` to ``dest`` until it reaches ``expected`` bytes."""
    for attempt in range(1, retries + 1):
        have = dest.stat().st_size if dest.exists() else 0
        if have == expected:
            print(f"  already complete ({human(have)})")
            return
        if have > expected:
            print(f"  local file larger than expected; restarting ({human(have)})")
            dest.unlink()
            have = 0

        headers = {"User-Agent": USER_AGENT}
        if have:
            headers["Range"] = f"bytes={have}-"
        req = urllib.request.Request(url, headers=headers)
        mode = "ab" if have else "wb"
        try:
            with urllib.request.urlopen(req, timeout=60) as resp, open(dest, mode) as fh:
                got = have
                t0 = time.time()
                while True:
                    block = resp.read(CHUNK)
                    if not block:
                        break
                    fh.write(block)
                    got += len(block)
                    secs = max(time.time() - t0, 1e-6)
                    rate = (got - have) / secs
                    pct = 100 * got / expected
                    print(
                        f"\r  {pct:5.1f}%  {human(got)} / {human(expected)}  "
                        f"{human(rate)}/s",
                        end="",
                        flush=True,
                    )
                print()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            print(f"\n  attempt {attempt}/{retries} failed: {exc}")
            time.sleep(min(5 * attempt, 20))
            continue

        size = dest.stat().st_size
        if size == expected:
            return
        print(f"  short read: {human(size)} of {human(expected)}; resuming")
        time.sleep(2)

    raise RuntimeError(f"could not download {url} after {retries} attempts")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quarters", nargs="*", help="subset, e.g. 2024_2 2025_1")
    ap.add_argument("--unzip", action="store_true", help="extract each zip after download")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    template = manifest["bulk_url_template"]
    entries = manifest["quarters"]
    if args.quarters:
        wanted = set(args.quarters)
        entries = [e for e in entries if e["quarter"] in wanted]
        missing = wanted - {e["quarter"] for e in entries}
        if missing:
            print(f"unknown quarter(s): {', '.join(sorted(missing))}", file=sys.stderr)
            return 2

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    total = sum(e["bytes"] for e in entries)
    print(f"Fetching {len(entries)} DB1B file(s) into {RAW_DIR}  ({human(total)} total)")

    for i, entry in enumerate(entries, 1):
        name, expected = entry["file"], entry["bytes"]
        dest = RAW_DIR / name
        print(f"\n[{i}/{len(entries)}] {entry['quarter']}  ({human(expected)})")
        download(template.format(quarter=entry["quarter"]), dest, expected)
        if args.unzip:
            print(f"  unzipping {name}")
            with zipfile.ZipFile(dest) as zf:
                zf.extractall(dest.with_suffix(""))

    print(f"\nDone. Files in {RAW_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
