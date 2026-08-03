#!/usr/bin/env python3
"""
weixin-ilink.py — 微信 iLink bot 纯 Python 客户端

功能：
1. getUpdates long-poll：维持 session 活跃，接收用户消息
2. sendMessage (tokenless)：不依赖 context_token 直接发送

用法：
  作为模块：from weixin_ilink import ILinkClient
  独立运行：python3 weixin-ilink.py --ping  # 发一条测试消息

设计原则：
  - 零 JS 依赖，纯 requests + json
  - tokenless 发送（iLink 在 session 活跃时允许）
  - getUpdates 维持 session 热度
"""

import argparse
import base64
import json
import logging
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger("weixin-ilink")

# ─── 配置 ───────────────────────────────────────────────

ACCOUNT_FILE = Path("/root/.openclaw/openclaw-weixin/accounts/999559c28b26-im-bot.json")
SYNC_FILE = Path("/root/.openclaw/openclaw-weixin/accounts/999559c28b26-im-bot.sync.json")

ILINK_APP_ID = "bot"
ILINK_APP_CLIENT_VERSION = 131336  # v2.1.8 → (2<<16)|(1<<8)|8
CHANNEL_VERSION = "2.1.8"

DEFAULT_TIMEOUT = 15  # seconds for regular API
LONG_POLL_TIMEOUT = 35  # seconds for getUpdates
TOKENLESS_MAX_RETRIES = 2
TOKENLESS_RETRY_DELAY = 1.0  # seconds


def load_account() -> dict[str, str]:
    """Load bot account credentials."""
    data = json.loads(ACCOUNT_FILE.read_text())
    return {
        "token": data["token"],
        "baseUrl": data.get("baseUrl", "https://ilinkai.weixin.qq.com"),
        "userId": data.get("userId", ""),
    }


def load_sync_buf() -> str:
    """Load the getUpdates cursor (get_updates_buf)."""
    if SYNC_FILE.exists():
        data = json.loads(SYNC_FILE.read_text())
        return data.get("get_updates_buf", "")
    return ""


def save_sync_buf(buf: str) -> None:
    """Persist the getUpdates cursor."""
    SYNC_FILE.write_text(json.dumps({"get_updates_buf": buf}))


def _random_uin() -> str:
    """X-WECHAT-UIN: random uint32 → decimal string → base64."""
    u32 = random.randint(0, 0xFFFFFFFF)
    return base64.b64encode(str(u32).encode()).decode()


def _build_headers(token: str, body_len: int) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "AuthorizationType": "ilink_bot_token",
        "Content-Length": str(body_len),
        "X-WECHAT-UIN": _random_uin(),
        "iLink-App-Id": ILINK_APP_ID,
        "iLink-App-ClientVersion": str(ILINK_APP_CLIENT_VERSION),
        "Authorization": f"Bearer {token}",
    }


# ─── 核心类 ─────────────────────────────────────────────


class ILinkClient:
    """Minimal iLink bot client — getUpdates + tokenless sendMessage."""

    def __init__(self, account: dict[str, str] | None = None):
        self.account = account or load_account()
        self.base_url = self.account["baseUrl"].rstrip("/")
        self.token = self.account["token"]
        self.sync_buf = load_sync_buf()

    # ── sendMessage (tokenless) ──

    def send_text(
        self,
        to: str,
        text: str,
        context_token: str | None = None,
        max_retries: int = TOKENLESS_MAX_RETRIES,
    ) -> dict[str, Any]:
        """
        Send a text message.

        Strategy:
        1. If context_token available, try with it first
        2. On failure (or no token), retry tokenless up to max_retries

        Returns: {"ok": bool, "message_id": str, "raw": response}
        """
        # Phase 1: try with context_token if available
        if context_token:
            result = self._send_once(to, text, context_token)
            if result["ok"]:
                logger.info(f"sendMessage: delivered with context_token to={to}")
                return result
            logger.warning(
                f"sendMessage: context_token failed (ret={result.get('ret')}), "
                f"falling back to tokenless"
            )

        # Phase 2: tokenless retries
        for attempt in range(1, max_retries + 1):
            result = self._send_once(to, text, context_token=None)
            if result["ok"]:
                if attempt > 1:
                    logger.info(f"sendMessage: tokenless succeeded on attempt {attempt}")
                else:
                    logger.info(f"sendMessage: tokenless succeeded for to={to}")
                return result

            logger.error(
                f"sendMessage: tokenless attempt {attempt}/{max_retries} failed "
                f"ret={result.get('ret')} errmsg={result.get('errmsg', '')}"
            )
            if attempt < max_retries:
                time.sleep(TOKENLESS_RETRY_DELAY)

        return result  # last failure

    def _send_once(
        self,
        to: str,
        text: str,
        context_token: str | None = None,
    ) -> dict[str, Any]:
        """Single send attempt. Returns normalized result dict."""
        client_id = f"py-{random.randint(100000, 999999)}"
        msg: dict[str, Any] = {
            "from_user_id": "",
            "to_user_id": to,
            "client_id": client_id,
            "message_type": 2,  # BOT
            "message_state": 1,  # FINISH (legacy: 1, new: 2; both work)
            "item_list": [{"type": 1, "text_item": {"text": text}}],
        }
        if context_token:
            msg["context_token"] = context_token

        body = {"msg": msg, "base_info": {"channel_version": CHANNEL_VERSION}}
        body_json = json.dumps(body)
        headers = _build_headers(self.token, len(body_json.encode()))

        try:
            resp = requests.post(
                f"{self.base_url}/ilink/bot/sendmessage",
                data=body_json,
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
            )
            raw = resp.text
            logger.debug(f"sendmessage: HTTP {resp.status_code} resp={raw[:300]}")

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                return {"ok": False, "error": f"HTTP {resp.status_code}: non-JSON response", "raw": raw}

            ret = data.get("ret", 0)
            if ret != 0:
                return {
                    "ok": False,
                    "ret": ret,
                    "errmsg": data.get("errmsg", "unknown"),
                    "raw": raw,
                }

            return {
                "ok": True,
                "message_id": str(data.get("message_id", "")),
                "raw": raw,
            }

        except requests.RequestException as e:
            return {"ok": False, "error": str(e), "raw": ""}

    # ── getUpdates (long-poll) ──

    def get_updates(self, timeout: int = LONG_POLL_TIMEOUT) -> dict[str, Any]:
        """
        Long-poll for new messages. Updates sync_buf automatically.

        Returns: {"ok": bool, "msgs": list, "get_updates_buf": str}
        """
        body = json.dumps({
            "get_updates_buf": self.sync_buf,
            "base_info": {"channel_version": CHANNEL_VERSION},
        })
        headers = _build_headers(self.token, len(body.encode()))

        try:
            resp = requests.post(
                f"{self.base_url}/ilink/bot/getupdates",
                data=body,
                headers=headers,
                timeout=timeout + 5,  # client timeout > server timeout
            )
            raw = resp.text
            data = json.loads(raw)

            ret = data.get("ret", 0)
            if ret != 0:
                errcode = data.get("errcode", "")
                errmsg = data.get("errmsg", "")
                logger.warning(f"getUpdates: ret={ret} errcode={errcode} errmsg={errmsg}")
                return {"ok": False, "ret": ret, "msgs": [], "get_updates_buf": self.sync_buf}

            new_buf = data.get("get_updates_buf", "")
            if new_buf:
                self.sync_buf = new_buf
                save_sync_buf(new_buf)

            msgs = data.get("msgs", [])
            return {"ok": True, "msgs": msgs, "get_updates_buf": self.sync_buf}

        except requests.Timeout:
            # Normal for long-poll
            return {"ok": True, "msgs": [], "get_updates_buf": self.sync_buf}
        except Exception as e:
            logger.error(f"getUpdates error: {e}")
            return {"ok": False, "error": str(e), "msgs": [], "get_updates_buf": self.sync_buf}

    # ── 便捷方法 ──

    def send_chunked(
        self,
        to: str,
        text: str,
        chunk_size: int = 800,
        context_token: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Send long text in chunks. Weixin tends to fold long messages.
        Returns list of results per chunk.
        """
        results = []
        chunks = []
        current = ""
        for line in text.split("\n"):
            if len(current) + len(line) + 1 > chunk_size and current:
                chunks.append(current)
                current = line
            else:
                current = current + "\n" + line if current else line
        if current:
            chunks.append(current)

        for i, chunk in enumerate(chunks):
            r = self.send_text(to, chunk.strip(), context_token=context_token)
            results.append(r)
            if not r["ok"]:
                logger.error(f"chunk {i+1}/{len(chunks)} failed, aborting")
                break
            if i < len(chunks) - 1:
                time.sleep(0.5)  # small delay between chunks

        return results

    def ping(self, to: str | None = None) -> bool:
        """Send a test message to verify connectivity."""
        to = to or self.account["userId"]
        result = self.send_text(to, "🏓 ping — weixin-ilink.py OK")
        return result["ok"]


# ─── CLI ────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Weixin iLink Python client")
    parser.add_argument("--ping", action="store_true", help="Send a test message")
    parser.add_argument("--send", type=str, help="Send a text message")
    parser.add_argument("--to", type=str, help="Recipient (default: account userId)")
    parser.add_argument("--poll", action="store_true", help="Run getUpdates long-poll loop")
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    client = ILinkClient()

    if args.ping:
        ok = client.ping(args.to)
        print(json.dumps({"ok": ok}))
        sys.exit(0 if ok else 1)

    if args.send:
        results = client.send_chunked(args.to or client.account["userId"], args.send)
        all_ok = all(r["ok"] for r in results)
        print(json.dumps({"ok": all_ok, "chunks": len(results)}, ensure_ascii=False))
        sys.exit(0 if all_ok else 1)

    if args.poll:
        logger.info("Starting getUpdates long-poll loop (Ctrl+C to stop)...")
        while True:
            result = client.get_updates()
            if result["ok"] and result["msgs"]:
                for msg in result["msgs"]:
                    from_uid = msg.get("from_user_id", "?")
                    items = msg.get("item_list", [])
                    text = ""
                    ctx_token = msg.get("context_token", "")
                    for item in items:
                        if item.get("type") == 1:
                            text = item.get("text_item", {}).get("text", "")
                    logger.info(f"inbound: from={from_uid} text={text[:80]} ctx_token={'yes' if ctx_token else 'no'}")
            elif not result["ok"]:
                logger.warning(f"getUpdates failed: {result.get('error', result.get('ret', '?'))}")
                time.sleep(5)

    parser.print_help()


if __name__ == "__main__":
    main()
