# XMON Discord Chat Exporter — v2.0 Pro

<p align="center">
  <img src="assets/xmon_logo.png" alt="XMON Logo" width="120" />
</p>

<p align="center">
  <b>A modern, high-performance, read-only Discord message archiving suite built with Python, Tkinter, and the official Discord REST API v10.</b>
</p>

<p align="center">
  <a href="https://xmon4u.github.io"><img src="https://img.shields.io/badge/Developer%20Portfolio-xmon4u.github.io-blue?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Portfolio"></a>
  <a href="https://github.com/Xmon4u"><img src="https://img.shields.io/badge/GitHub-Xmon4u-181717?style=for-the-badge&logo=github" alt="GitHub"></a>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/API-Discord%20REST%20v10-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord API">
</p>

---

## 🌟 Key Highlights & Features

- 🛡️ **100% In-Memory Security**: Your Discord Bot Token is never written to disk, registry, or any remote server. It stays purely in memory during your active session.
- 📖 **Strictly Read-Only**: Compliant with official Discord Bot API terms. Never sends, edits, deletes, or modifies any messages.
- ⚡ **Multi-View Dashboard**:
  - **📤 Exporter**: Full-featured export suite with live progress indicators and instant cancellation support.
  - **📋 Dedicated Logs**: Real-time log inspector with instant search/filter, clipboard copying, and export to `.log` file.
  - **⚙️ Settings**: Configurable request throttling (Turbo, Standard, Safe, Ultra-Safe) and customizable default export settings.
  - **👤 About Me**: Dedicated creator showcase featuring developer profile, bio, system specs, and direct links to **[xmon4u.github.io](https://xmon4u.github.io)**.
  - **◎ Support**: Interactive step-by-step bot setup tutorial and common error resolution guide.
- 🔍 **Flexible Filtering Modes**:
  - **All Messages**: Complete channel history export.
  - **Webhook Only**: Extracts only automated webhook broadcasts.
  - **Specific Webhook**: Target an exact webhook by display name.
- 📁 **Export Formats**:
  - **TXT**: Pristine formatting with uniform multiline message indentation.
  - **JSON**: Structured schema containing IDs, timestamps, authors, embeds, stickers, and attachment URLs.
  - **CSV**: Spreadsheet-ready tabular dataset for Microsoft Excel or Google Sheets.
- 🛑 **Live Cancellation**: Safely stop an export at any point without corrupting partially retrieved data.
- 🖥️ **High-DPI Razor Sharp UI**: Custom Windows DWM immersive dark title bar and Per-Monitor DPI font rendering.

---

## 🗂️ Project Structure

```
Discord-Chat-Exporter/
│
├── assets/                 # Brand assets, icons & graphics
│   ├── avatar.png          # Developer profile avatar
│   ├── xmon_logo.png       # Primary XMON emblem
│   └── xmon_logo_gen.png   # High-resolution banner graphic
├── docs/                   # Documentation & setup guides
│   └── BOT_PERMISSIONS.txt # Detailed Discord bot permissions breakdown
├── main.py                 # Multi-view desktop GUI application
├── exporter.py             # Official Discord REST API v10 extraction pipeline
├── Start XMON Exporter.bat # One-click Windows desktop launcher
├── requirements.txt        # Python library dependencies
├── .gitignore              # Standard Git exclusion definitions
├── .gitattributes         # Text normalization & line-ending controls
└── README.md               # Project documentation & reference
```

---

## 🚀 Step-by-Step Windows Setup

### 1. Requirements
- **Windows 10 / 11** (64-bit recommended)
- **Python 3.10+** (ensure **"Add Python to PATH"** is checked during setup)

### 2. Installation
Open Command Prompt or PowerShell in the project directory:

```bash
pip install -r requirements.txt
```

### 3. Launching
You can launch the application by double-clicking **`Start XMON Exporter.bat`** or via terminal:

```bash
python main.py
```

---

## 🤖 Discord Bot Quick Start Guide

1. **Create an Application**:
   - Navigate to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Click **"New Application"**, assign a name (e.g. `XMON Exporter`), and create it.

2. **Enable Privileged Gateway Intents**:
   - Go to the **Bot** tab on the left sidebar.
   - Scroll down to **Privileged Gateway Intents** and enable:
     - ✅ **Message Content Intent**
   - Click **Save Changes**.

3. **Get Your Bot Token**:
   - In the **Bot** tab, click **"Reset Token"** and copy the generated token.
   - *Never share your bot token with unauthorized parties.*

4. **Invite Bot to Your Server**:
   - Go to **OAuth2 → URL Generator**.
   - Check scope: `bot`.
   - Check permissions:
     - ✅ `View Channels`
     - ✅ `Read Message History`
   - Copy the authorization URL generated at the bottom and open it in your browser to invite the bot to your server.

5. **Copy Channel ID**:
   - In Discord Settings → **Advanced** → enable **Developer Mode**.
   - Right-click any channel you want to archive → click **"Copy Channel ID"** (or paste the channel URL directly into XMON; it will auto-extract the ID).

---

## 👤 Developer & Creator

**Created by XMON** — Founder & Lead Developer at **XMON Corporation**.

- 🌐 **Official Website / Portfolio**: **[https://xmon4u.github.io](https://xmon4u.github.io)**
- 🐙 **GitHub Profile**: **[https://github.com/Xmon4u](https://github.com/Xmon4u)**

---

## 🛡️ Privacy & Legal Disclaimer

- **XMON Discord Chat Exporter** is an independent utility and is not affiliated with, authorized, maintained, or endorsed by Discord Inc.
- All requests use the official, documented **Discord REST API v10**.
- The software does not use user tokens ("self-bots") and is completely read-only.
- All user tokens and channel contents stay strictly on the user's local machine.

---

<p align="center">
  <sub>© 2026 XMON Corporation. All rights reserved.</sub>
</p>
