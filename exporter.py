"""
XMON Discord Chat Exporter — Core Logic v2.0
Branded by XMON  |  Uses the official Discord REST API v10 (bot token).
Read-only operation: No messages are sent, edited, deleted, or stored externally.
"""

import requests
import time
import json
import csv
import os
import re
import threading
from datetime import datetime, timezone


DISCORD_API_BASE = "https://discord.com/api/v10"


def sanitize_token(token: str) -> str:
    """Clean and sanitize Discord bot token input."""
    if not token:
        return ""
    cleaned = token.strip().strip("'\"")
    if cleaned.lower().startswith("bot "):
        cleaned = cleaned[4:].strip()
    return cleaned


def sanitize_channel_id(channel_input: str) -> str:
    """
    Extract clean numeric Channel Snowflake ID.
    Handles raw IDs or copied channel URLs (e.g. discord.com/channels/guild/channel).
    """
    if not channel_input:
        return ""
    cleaned = channel_input.strip().strip("'\"")
    # Check if a URL was pasted
    match = re.search(r"/channels/(?:@me|\d+)/(\d+)", cleaned)
    if match:
        return match.group(1)
    # Check for direct numeric string
    digits = re.findall(r"\d+", cleaned)
    if digits:
        # Return the longest contiguous digit sequence if user had extra characters
        return max(digits, key=len)
    return cleaned


class DiscordExporter:
    """Fetches and exports messages from a Discord channel via the REST API."""

    def __init__(
        self,
        bot_token: str,
        channel_id: str,
        progress_callback=None,
        cancel_event: threading.Event = None,
        request_delay: float = 0.4
    ):
        clean_token = sanitize_token(bot_token)
        clean_channel = sanitize_channel_id(channel_id)

        if not clean_token or not clean_channel:
            raise ValueError("Bot token and Channel ID must not be empty.")

        self.bot_token = clean_token
        self.channel_id = clean_channel
        self.progress_callback = progress_callback  # callable(msg: str, tag: str = "info")
        self.cancel_event = cancel_event
        self.request_delay = max(0.1, min(float(request_delay), 3.0))

        self.headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json",
            "User-Agent": "XMONDiscordExporter/2.0 (Windows; Python; XMON Corp)"
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _log(self, msg: str, tag: str = "info"):
        if self.progress_callback:
            try:
                self.progress_callback(msg, tag)
            except TypeError:
                self.progress_callback(msg)

    def _is_cancelled(self) -> bool:
        return bool(self.cancel_event and self.cancel_event.is_set())

    def _get(self, endpoint: str, params: dict = None) -> requests.Response:
        url = f"{DISCORD_API_BASE}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        return response

    def _check_permissions(self) -> dict:
        """Verify the bot can access the channel and has read history permission."""
        resp = self._get(f"/channels/{self.channel_id}")
        if resp.status_code == 401:
            raise PermissionError(
                "Invalid bot token (401 Unauthorized).\n"
                "Please verify your token in the Discord Developer Portal."
            )
        if resp.status_code == 403:
            raise PermissionError(
                "Bot does not have permission to access this channel (403 Forbidden).\n"
                "Ensure the bot is added to this server with 'View Channels' and 'Read Message History'."
            )
        if resp.status_code == 404:
            raise ValueError(
                f"Channel '{self.channel_id}' was not found (404 Not Found).\n"
                "Please check that the Channel ID is correct and the bot has access to it."
            )
        if not resp.ok:
            raise ConnectionError(
                f"Discord API Error {resp.status_code}: {resp.text}"
            )
        try:
            return resp.json()
        except Exception:
            return {}

    # ------------------------------------------------------------------
    # Message fetching
    # ------------------------------------------------------------------

    def fetch_all_messages(self) -> list[dict]:
        """
        Retrieve messages from the channel in chronological order.
        Handles pagination, rate limits, and user cancellation.
        Returns a list of raw Discord message dicts.
        """
        ch_data = self._check_permissions()
        ch_name = ch_data.get("name", self.channel_id)
        self._log(f"Channel verified: #{ch_name} (ID: {self.channel_id})", "info")
        self._log("Permission check passed. Starting message retrieval...", "info")

        all_messages = []
        last_id = None
        batch_num = 0

        while True:
            if self._is_cancelled():
                self._log("⚠️ Export stopped by user request.", "warning")
                break

            params = {"limit": 100}
            if last_id:
                params["before"] = last_id

            resp = self._get(f"/channels/{self.channel_id}/messages", params=params)

            # Handle rate limiting (429)
            if resp.status_code == 429:
                try:
                    retry_data = resp.json()
                    retry_after = float(retry_data.get("retry_after", 1.0))
                except Exception:
                    retry_after = 1.0
                self._log(f"⏳ Rate limited. Backing off for {retry_after:.1f}s...", "warning")
                time.sleep(retry_after + 0.1)
                continue

            if resp.status_code == 403:
                raise PermissionError(
                    "Bot lost 'Read Message History' permission while fetching messages."
                )
            if not resp.ok:
                raise ConnectionError(
                    f"API error {resp.status_code} while fetching messages: {resp.text}"
                )

            batch = resp.json()
            if not batch:
                break

            batch_num += 1
            all_messages.extend(batch)
            last_id = batch[-1]["id"]

            self._log(
                f"Fetched batch {batch_num}: +{len(batch)} messages "
                f"(total: {len(all_messages)})",
                "info"
            )

            # Check cancellation right after batch
            if self._is_cancelled():
                self._log("⚠️ Export stopped by user request.", "warning")
                break

            # Polite throttle delay
            time.sleep(self.request_delay)

            if len(batch) < 100:
                break  # Reached the very beginning of the channel

        # Discord returns newest-first; reverse to chronological order
        all_messages.reverse()
        self._log(f"Retrieval complete. Total retrieved: {len(all_messages)} messages.", "info")
        return all_messages

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    @staticmethod
    def filter_messages(
        messages: list[dict],
        mode: str,                  # "all" | "webhook_only" | "specific_webhook"
        specific_webhook_name: str = ""
    ) -> list[dict]:
        """
        Filter the raw message list according to the export mode.
          - "all"              : return every message
          - "webhook_only"     : return messages sent via any webhook
          - "specific_webhook" : return messages from a specific webhook name (case-insensitive)
        """
        if mode == "all":
            return messages

        filtered = []
        target_name = specific_webhook_name.strip().lower()

        for msg in messages:
            is_webhook = bool(msg.get("webhook_id"))
            if mode == "webhook_only" and is_webhook:
                filtered.append(msg)
            elif mode == "specific_webhook" and is_webhook:
                author_name = msg.get("author", {}).get("username", "")
                if author_name.lower() == target_name:
                    filtered.append(msg)

        return filtered

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _format_message(msg: dict) -> dict:
        """Convert a raw Discord API message dict to standard export schema."""
        author = msg.get("author", {})
        author_name = author.get("username", "Unknown")
        discriminator = author.get("discriminator", "0000")
        if discriminator not in ("0", "0000", "", None):
            author_name += f"#{discriminator}"

        # Collect attachment URLs, embeds, sticker URLs
        attachments = [a.get("url", "") for a in msg.get("attachments", []) if a.get("url")]
        embed_urls = []
        for embed in msg.get("embeds", []):
            if embed.get("url"):
                embed_urls.append(embed["url"])
            if embed.get("image", {}).get("url"):
                embed_urls.append(embed["image"]["url"])
            if embed.get("thumbnail", {}).get("url"):
                embed_urls.append(embed["thumbnail"]["url"])
        
        # Sticker items
        sticker_urls = [
            f"https://media.discordapp.net/stickers/{s.get('id')}.png"
            for s in msg.get("sticker_items", []) if s.get("id")
        ]

        all_urls = list(dict.fromkeys(attachments + embed_urls + sticker_urls))

        # Parse ISO-8601 timestamp
        raw_ts = msg.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
            formatted_time = dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            formatted_time = raw_ts

        return {
            "message_id": msg.get("id", ""),
            "channel_id": msg.get("channel_id", ""),
            "author": author_name,
            "webhook_id": msg.get("webhook_id", "") or "",
            "content": msg.get("content", "") or "",
            "timestamp": formatted_time,
            "attachments_urls": " | ".join(all_urls) if all_urls else "",
        }

    # ------------------------------------------------------------------
    # Export writers
    # ------------------------------------------------------------------

    @staticmethod
    def export_txt(messages: list[dict], filepath: str) -> None:
        """Write human-readable TXT file with uniform multiline indentation."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"=== XMON DISCORD EXPORT | Total Messages: {len(messages)} ===\n\n")
            for msg in messages:
                f.write(f"[{msg['timestamp']}] {msg['author']}\n")
                if msg["content"]:
                    for line in msg["content"].splitlines():
                        f.write(f"  {line}\n")
                if msg["attachments_urls"]:
                    f.write(f"  Attachments: {msg['attachments_urls']}\n")
                f.write(
                    f"  (Message ID: {msg['message_id']} | Channel ID: {msg['channel_id']})\n"
                )
                f.write("-" * 60 + "\n")

    @staticmethod
    def export_json(messages: list[dict], filepath: str) -> None:
        """Write clean, indented JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_csv(messages: list[dict], filepath: str) -> None:
        """Write spreadsheet-compatible CSV file (always writes header even if empty)."""
        fieldnames = [
            "message_id", "channel_id", "author", "webhook_id",
            "timestamp", "content", "attachments_urls"
        ]
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            if messages:
                writer.writerows(messages)

    # ------------------------------------------------------------------
    # Public export pipeline
    # ------------------------------------------------------------------

    def export(
        self,
        output_path: str,
        fmt: str,               # "txt" | "json" | "csv"
        mode: str,              # "all" | "webhook_only" | "specific_webhook"
        specific_webhook: str = ""
    ) -> str:
        """
        Full pipeline: fetch → filter → format → save.
        Returns the absolute path of the written file.
        """
        raw = self.fetch_all_messages()

        if self._is_cancelled() and not raw:
            raise InterruptedError("Export cancelled by user before any messages were retrieved.")

        self._log(f"Applying filter: {mode}...", "info")
        filtered = self.filter_messages(raw, mode, specific_webhook)
        self._log(f"{len(filtered)} matching messages after filter.", "info")

        self._log("Formatting messages...", "info")
        formatted = [self._format_message(m) for m in filtered]

        os.makedirs(output_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{self.channel_id}_{timestamp}.{fmt.lower()}"
        filepath = os.path.join(output_path, filename)

        self._log(f"Writing {fmt.upper()} file: {filename}", "info")
        if fmt.lower() == "txt":
            self.export_txt(formatted, filepath)
        elif fmt.lower() == "json":
            self.export_json(formatted, filepath)
        elif fmt.lower() == "csv":
            self.export_csv(formatted, filepath)
        else:
            raise ValueError(f"Unknown format: {fmt}")

        status_msg = f"Export complete! Saved {len(formatted)} messages to: {filepath}"
        if self._is_cancelled():
            status_msg = f"Partial export saved ({len(formatted)} messages): {filepath}"
        self._log(f"✅ {status_msg}", "success")
        return filepath
