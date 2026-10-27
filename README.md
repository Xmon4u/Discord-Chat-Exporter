# Discord Chat Exporter

A desktop application for archiving and exporting Discord channel message history using Python, Tkinter, and the official Discord REST API v10.

## Overview

Discord Chat Exporter connects via a standard Discord Bot account to retrieve channel history and export it into clean text, JSON, or CSV files. The application runs entirely on your local machine and operates in read-only mode.

## Features

- **Read-Only API Access**: Uses the official Discord REST API v10 without modifying, posting, or deleting server messages.
- **Multiple Export Formats**:
  - **TXT**: Clean, indented readable transcript with timestamps and user names.
  - **JSON**: Structured message objects including message IDs, timestamps, authors, embeds, attachments, and reactions.
  - **CSV**: Tabular rows formatted for Excel or spreadsheet analysis.
- **Message Filtering**: Export complete channel history or filter specifically by webhooks and bots.
- **Configurable Rate Limiting**: Adjust request throttling to avoid Discord API rate limits during large channel exports.
- **Live Activity Log**: Real-time console showing API requests, progress percentage, and error diagnostics.
- **Local Security**: Bot tokens are stored in memory only during your active session and are not written to disk or sent to external servers.

## Installation & Setup

### Requirements
- Windows 10 / 11 (or Linux / macOS with Tkinter)
- Python 3.10 or newer

### Installation

```bash
# Clone the repository
git clone https://github.com/Xmon4u/Discord-Chat-Exporter.git
cd Discord-Chat-Exporter

# Install dependencies
pip install -r requirements.txt

# Launch the application
python main.py
```

*Windows users can also launch directly by double-clicking `Start XMON Exporter.bat`.*

## Discord Bot Setup Guide

To export channel messages, you need a Discord bot in your server:

1. **Create an Application**:
   - Open the [Discord Developer Portal](https://discord.com/developers/applications).
   - Click **New Application** and enter a name (e.g., `Chat Exporter`).

2. **Enable Message Content Intent**:
   - In the left sidebar, navigate to **Bot**.
   - Scroll down to **Privileged Gateway Intents** and enable **Message Content Intent**.
   - Click **Save Changes**.

3. **Copy the Bot Token**:
   - Under the **Bot** tab, click **Reset Token** and copy your token. Keep this token private.

4. **Invite the Bot to Your Server**:
   - Navigate to **OAuth2** > **URL Generator**.
   - Under **Scopes**, select `bot`.
   - Under **Bot Permissions**, check `View Channels` and `Read Message History`.
   - Copy the generated URL, open it in your browser, and authorize the bot for your server.

5. **Get Channel ID**:
   - In your Discord client, open **Settings** > **Advanced** and enable **Developer Mode**.
   - Right-click the channel you wish to export and select **Copy Channel ID**.
   - Paste the Channel ID (or channel URL) into the exporter interface.

## Project Structure

```text
Discord-Chat-Exporter/
├── assets/                 # UI icons and graphic assets
├── docs/                   # Setup guides and permissions reference
├── main.py                 # Tkinter graphical user interface
├── exporter.py             # Discord REST API message fetcher and parsers
├── Start XMON Exporter.bat # Windows desktop launcher
├── requirements.txt        # Python dependencies
└── README.md
```

## Disclaimer

This project is an independent open-source utility and is not affiliated with or endorsed by Discord Inc. Always ensure you have appropriate permissions from server owners before exporting message archives.

## License

This project is licensed under the MIT License.
