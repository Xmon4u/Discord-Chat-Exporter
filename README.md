# XMON Discord Chat Exporter — v2.0 Pro

<p align="center">
  <img src="assets/xmon_logo.png" alt="XMON Logo" width="120" />
</p>

<p align="center">
  <b>A high-performance, read-only Discord message archiving application built with Python, Tkinter, and the official Discord REST API v10.</b>
</p>

<p align="center">
  <a href="https://xmon4u.github.io"><img src="https://img.shields.io/badge/Developer%20Portfolio-xmon4u.github.io-blue?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Portfolio"></a>
  <a href="https://github.com/Xmon4u"><img src="https://img.shields.io/badge/GitHub-Xmon4u-181717?style=for-the-badge&logo=github" alt="GitHub"></a>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/API-Discord%20REST%20v10-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord API">
</p>

---

## Key Features

- **In-Memory Security**: Your Discord Bot Token is never written to disk, the registry, or any remote server. It stays in memory only for the duration of your active session.
- **Strictly Read-Only**: Compliant with official Discord Bot API terms. The application never sends, edits, deletes, or modifies any messages.
- **Multi-View Dashboard**:
  - **Exporter**: Full-featured export suite with live progress indicators and instant cancellation support.
  - **Logs**: Real-time log inspector with instant search/filter, clipboard copying, and export to `.log` file.
  - **Settings**: Configurable request throttling (Turbo, Standard, Safe, Ultra-Safe) and customizable default export settings.
  - **About**: Developer profile, bio, system specs, and links to [xmon4u.github.io](https://xmon4u.github.io).
  - **Support**: Step-by-step bot setup tutorial and common error resolution guide.
- **Flexible Filtering Modes**:
  - **All Messages**: Complete channel history export.
  - **Webhook Only**: Extracts only automated webhook broadcasts.
  - **Specific Webhook**: Target an exact webhook by display name.
- **Export Formats**:
  - **TXT**: Clean formatting with uniform multiline message indentation.
  - **JSON**: Structured schema containing IDs, timestamps, authors, embeds, stickers, and attachment URLs.
  - **CSV**: Spreadsheet-ready tabular dataset for Microsoft Excel or Google Sheets.
- **Live Cancellation**: Safely stop an export at any point without corrupting partially retrieved data.
- **High-DPI UI**: Custom Windows DWM dark title bar with per-monitor DPI font rendering.

---

## Project Structure

```
Discord-Chat-Exporter/
│
├── assets/                 # Brand assets, icons & graphics
│   ├── avatar.png          # Developer profile avatar
│   ├── xmon_logo.png       # Primary XMON emblem
│   └── xmon_logo_gen.png   # High-resolution banner graphic
├── docs/                   # Documentation & setup guides
│   └── BOT_PERMISSIONS.txt # Discord bot permissions breakdown
├── main.py                 # Multi-view desktop GUI application
├── exporter.py             # Discord REST API v10 extraction pipeline
├── Start XMON Exporter.bat # One-click Windows desktop launcher
├── requirements.txt        # Python library dependencies
├── .gitignore              # Git exclusion definitions
├── .gitattributes          # Text normalization & line-ending controls
└── README.md               # Project documentation
```

---

## Setup (Windows)

### Requirements
- **Windows 10 / 11** (64-bit)
- **Python 3.10+** (ensure "Add Python to PATH" is checked during setup)

### Installation
Open Command Prompt or PowerShell in the project directory:

```bash
pip install -r requirements.txt
```

### Running
Double-click **`Start XMON Exporter.bat`** or launch via terminal:

```bash
python main.py
```

---

## Discord Bot Setup

1. **Create an Application**:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Click **"New Application"**, give it a name (e.g. `XMON Exporter`), and confirm.

2. **Enable Privileged Gateway Intents**:
   - Go to the **Bot** tab.
   - Under **Privileged Gateway Intents**, enable **Message Content Intent**.
   - Click **Save Changes**.

3. **Get Your Bot Token**:
   - In the **Bot** tab, click **"Reset Token"** and copy the generated token.
   - Do not share your bot token with anyone.

4. **Invite Bot to Your Server**:
   - Go to **OAuth2 → URL Generator**.
   - Check scope: `bot`.
   - Check permissions: `View Channels` and `Read Message History`.
   - Open the generated URL in your browser to invite the bot.

5. **Copy Channel ID**:
   - In Discord Settings → **Advanced** → enable **Developer Mode**.
   - Right-click any channel → **Copy Channel ID** (or paste the channel URL directly into XMON; it extracts the ID automatically).

---

## Developer

**Created by XMON** — Founder & Lead Developer at XMON Corporation.

- Website / Portfolio: [https://xmon4u.github.io](https://xmon4u.github.io)
- GitHub: [https://github.com/Xmon4u](https://github.com/Xmon4u)

---

## Privacy & Legal Disclaimer

- **XMON Discord Chat Exporter** is an independent utility and is not affiliated with, authorized, maintained, or endorsed by Discord Inc.
- All requests use the official **Discord REST API v10**.
- The software does not use user tokens (self-bots) and is completely read-only.
- All tokens and channel contents remain strictly on the user's local machine.

---

<p align="center">
  <sub>© 2026 XMON Corporation. All rights reserved.</sub>
</p>
