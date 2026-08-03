#!/usr/bin/env python3
"""
deliver.py — 微信 iLink tokenless 投递工具

用法:
  python3 deliver.py "要发送的文本"
  echo "文本内容" | python3 deliver.py --stdin

被其他脚本 import:
  from deliver import deliver_text
  ok = deliver_text("内容", chunk_size=800)
"""

import sys
import os
import logging

# 添加脚本目录到 path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from weixin_ilink import ILinkClient

logger = logging.getLogger("deliver")


def deliver_text(text: str, chunk_size: int = 800) -> bool:
    """
    通过 tokenless 方式投递文本到微信。
    长文本自动分段发送。

    Returns: True if all chunks delivered successfully.
    """
    client = ILinkClient()
    to = client.account["userId"]

    results = client.send_chunked(to, text, chunk_size=chunk_size)
    all_ok = all(r.get("ok", False) for r in results)

    if all_ok:
        logger.info(f"✅ Delivered {len(results)} chunks to {to}")
    else:
        failed = sum(1 for r in results if not r.get("ok", False))
        logger.error(f"❌ {failed}/{len(results)} chunks failed")

    return all_ok


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Weixin tokenless deliver")
    parser.add_argument("text", nargs="?", help="Text to send")
    parser.add_argument("--stdin", action="store_true", help="Read text from stdin")
    parser.add_argument("--chunk-size", type=int, default=800, help="Max chars per chunk")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.stdin:
        text = sys.stdin.read().strip()
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        sys.exit(1)

    if not text:
        print("Error: empty text", file=sys.stderr)
        sys.exit(1)

    ok = deliver_text(text, chunk_size=args.chunk_size)
    print("OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
