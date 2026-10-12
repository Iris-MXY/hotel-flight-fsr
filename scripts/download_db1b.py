"""下载本项目使用的 13 个季度美国交通部 DB1B（Market）原始文件。

原始压缩包每个 78–105 MB（合计约 1.27 GB），因此**不存入本仓库**。
本脚本把它们下载到 ``data/raw/db1b/``（已被 gitignore），并按
``data/flight/db1b_manifest.json`` 中记录的字节数逐个校验，可选地就地解压。

下载支持断点续传：若存在未完成的文件，只请求剩余字节，因此可随时中断后重新运行。
BTS 有时较慢并会断开连接，重新运行脚本即可继续。

用法：
    python scripts/download_db1b.py                 # 下载 + 校验，不解压
    python scripts/download_db1b.py --unzip         # 同时解压出 CSV
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
    """把 ``url`` 断点续传到 ``dest``，直到达到 ``expected`` 字节。"""
    for attempt in range(1, retries + 1):
        have = dest.stat().st_size if dest.exists() else 0
        if have == expected:
            print(f"  已完整（{human(have)}）")
            return
        if have > expected:
            print(f"  本地文件大于预期，重新下载（{human(have)}）")
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
            print(f"\n  第 {attempt}/{retries} 次尝试失败：{exc}")
            time.sleep(min(5 * attempt, 20))
            continue

        size = dest.stat().st_size
        if size == expected:
            return
        print(f"  读取不完整：{human(size)} / {human(expected)}，继续续传")
        time.sleep(2)

    raise RuntimeError(f"{url} 在 {retries} 次尝试后仍未下载完成")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quarters", nargs="*", help="子集，例如 2024_2 2025_1")
    ap.add_argument("--unzip", action="store_true", help="下载后解压每个压缩包")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    template = manifest["bulk_url_template"]
    entries = manifest["quarters"]
    if args.quarters:
        wanted = set(args.quarters)
        entries = [e for e in entries if e["quarter"] in wanted]
        missing = wanted - {e["quarter"] for e in entries}
        if missing:
            print(f"未知季度：{', '.join(sorted(missing))}", file=sys.stderr)
            return 2

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    total = sum(e["bytes"] for e in entries)
    print(f"准备下载 {len(entries)} 个 DB1B 文件到 {RAW_DIR}（共 {human(total)}）")

    for i, entry in enumerate(entries, 1):
        name, expected = entry["file"], entry["bytes"]
        dest = RAW_DIR / name
        print(f"\n[{i}/{len(entries)}] {entry['quarter']}  （{human(expected)}）")
        download(template.format(quarter=entry["quarter"]), dest, expected)
        if args.unzip:
            print(f"  解压 {name}")
            with zipfile.ZipFile(dest) as zf:
                zf.extractall(dest.with_suffix(""))

    print(f"\n完成。文件位于 {RAW_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
