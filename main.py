"""
XMON Discord Chat Exporter — Premium UI v2.0 Pro
XMON Corporation  |  Professional Desktop Application
Author / Developer: XMON (https://xmon4u.github.io  |  https://github.com/Xmon4u)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import json
import webbrowser
import platform

from exporter import DiscordExporter, sanitize_token, sanitize_channel_id

# ─────────────────────────────────────────────────────────────────────────────
# High-DPI scaling for Windows 10/11
# ─────────────────────────────────────────────────────────────────────────────
try:
    import ctypes
    # Per-monitor DPI awareness (1 = system, 2 = per-monitor)
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Optional Pillow acceleration for avatars and logos
try:
    from PIL import Image, ImageTk, ImageDraw
    PIL = True
except ImportError:
    PIL = False

# ─────────────────────────────────────────────────────────────────────────────
# Brand constants & links
# ─────────────────────────────────────────────────────────────────────────────
BRAND_NAME    = "XMON"
APP_TITLE     = "XMON Discord Chat Exporter"
APP_VER       = "v2.0.0 Pro"
WEBSITE_URL   = "https://xmon4u.github.io"
GITHUB_URL    = "https://github.com/Xmon4u"
DISCORD_DEV   = "https://discord.com/developers/applications"
CONFIG_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

LOGO_FILE     = "xmon_logo.png"
AVATAR_FILE   = "avatar.png"
SIDEBAR_WIDTH = 84

# ─────────────────────────────────────────────────────────────────────────────
# Curated Palette — XMON Monochrome / Silver / Deep Black
# ─────────────────────────────────────────────────────────────────────────────
APP_BG   = "#080808"     # Ultra-deep window background
SIDE_BG  = "#0b0b0b"     # Sidebar background
HDR_BG   = "#0d0d0d"     # Header canvas
CARD_BG  = "#111111"     # Primary card surface
CARD_BG2 = "#0e0e0e"     # Inactive / secondary surface
INP_BG   = "#070707"     # Input entry background
SEL_BG   = "#1c1c1c"     # Selected card/item background

BORDER   = "#1f1f1f"     # Subtle border
BORDER_F = "#3c3c3c"     # Focused / hover border
BORDER_D = "#141414"     # Dim divider

SIL      = "#b8b8b8"     # XMON signature silver
SIL_HI   = "#ffffff"     # Pure white highlight
SIL_HOV  = "#e4e4e4"     # Silver hover
SIL_DIM  = "#555555"     # Dim silver / muted accent

OK_COL   = "#3ddc84"     # Success green
WRN_COL  = "#e09820"     # Warning amber
ERR_COL  = "#e05252"     # Error red

TXT_1    = "#f4f4f4"     # Primary text (crisp light)
TXT_2    = "#b4b4b4"     # Secondary text (silver gray)
TXT_3    = "#686868"     # Muted text
TXT_4    = "#323232"     # Ghost text

# ─────────────────────────────────────────────────────────────────────────────
# Typography
# ─────────────────────────────────────────────────────────────────────────────
FONT_H1  = ("Segoe UI", 16, "bold")
FONT_H2  = ("Segoe UI", 11, "bold")
FONT_H3  = ("Segoe UI", 10, "bold")
FONT_B   = ("Segoe UI", 10)
FONT_SM  = ("Segoe UI", 9)
FONT_TIN = ("Segoe UI", 8)
FONT_MON = ("Consolas", 9)
FONT_BTN = ("Segoe UI", 10, "bold")
FONT_NAV = ("Segoe UI", 8)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers & Image Utilities
# ─────────────────────────────────────────────────────────────────────────────
def _find_file(filename: str) -> str | None:
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    return p if os.path.isfile(p) else None


# Cache for resized images to prevent stutter during window resize
_IMG_CACHE = {}


def _get_circle_avatar(path: str, size: int):
    """Crop image to a pristine antialiased circular avatar."""
    if not PIL or not path or not os.path.isfile(path):
        return None
    key = ("circle", path, size)
    if key in _IMG_CACHE:
        return _IMG_CACHE[key]
    try:
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        m = min(w, h)
        img = img.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m))
        img = img.resize((size, size), Image.LANCZOS)

        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)

        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        out.paste(img, mask=mask)
        tk_img = ImageTk.PhotoImage(out)
        _IMG_CACHE[key] = tk_img
        return tk_img
    except Exception:
        return None


def _get_watermark(path: str, size: int, alpha: float):
    """Load, resize, and apply opacity for header watermark with memoization."""
    if not PIL or not path or not os.path.isfile(path):
        return None
    # Round size to nearest 20px to reuse cached textures during continuous resize
    rounded_sz = (size // 20) * 20
    key = ("watermark", path, rounded_sz, alpha)
    if key in _IMG_CACHE:
        return _IMG_CACHE[key]
    try:
        img = Image.open(path).convert("RGBA").resize((rounded_sz, rounded_sz), Image.LANCZOS)
        r, g, b, a = img.split()
        a = a.point(lambda p: int(p * alpha))
        img.putalpha(a)
        tk_img = ImageTk.PhotoImage(img)
        _IMG_CACHE[key] = tk_img
        return tk_img
    except Exception:
        return None


def _get_logo(path: str, size: int):
    if not PIL or not path or not os.path.isfile(path):
        return None
    key = ("logo", path, size)
    if key in _IMG_CACHE:
        return _IMG_CACHE[key]
    try:
        img = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        _IMG_CACHE[key] = tk_img
        return tk_img
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Tooltip component
# ─────────────────────────────────────────────────────────────────────────────
class Tooltip:
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self._tip_win = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
        widget.bind("<ButtonPress>", self.hide)

    def show(self, _=None):
        if self._tip_win:
            return
        x = self.widget.winfo_rootx() + 8
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self._tip_win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        tk.Label(
            tw, text=self.text, font=FONT_TIN, fg=TXT_2, bg="#161616",
            relief="flat", bd=0, padx=8, pady=4,
            highlightthickness=1, highlightbackground=BORDER_F
        ).pack()

    def hide(self, _=None):
        if self._tip_win:
            self._tip_win.destroy()
            self._tip_win = None


# ─────────────────────────────────────────────────────────────────────────────
# Main Application Window
# ─────────────────────────────────────────────────────────────────────────────
class XMONApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(f"{BRAND_NAME}  ·  Discord Chat Exporter  ·  {APP_VER}")
        self.geometry("940x880")
        self.minsize(760, 600)
        self.configure(bg=APP_BG)

        # Retain references to PhotoImages
        self._img_refs = {}

        # Runtime state
        self._active_tab = "exporter"
        self._nav_widgets = {}
        self._views = {}
        self._export_thread = None
        self._cancel_event = threading.Event()
        self._is_exporting = False
        self._show_tok = False

        # Configuration settings
        self.config_data = self._load_config()

        # Visual elements
        self._setup_window_decorations()
        self._build_layout()
        self._switch_tab("exporter")

    # ── Config Persistence ───────────────────────────────────────────────────

    def _load_config(self) -> dict:
        default_cfg = {
            "output_folder": os.path.expanduser("~\\Desktop"),
            "default_format": "txt",
            "request_delay": 0.4,
            "auto_open_folder": True
        }
        if os.path.isfile(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    user_cfg = json.load(f)
                    default_cfg.update(user_cfg)
            except Exception:
                pass
        return default_cfg

    def _save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2)
        except Exception:
            pass

    # ── Window setup ─────────────────────────────────────────────────────────

    def _setup_window_decorations(self):
        # Set App Icon
        logo_path = _find_file(LOGO_FILE)
        if logo_path and PIL:
            try:
                raw_icon = Image.open(logo_path).resize((32, 32), Image.LANCZOS)
                tk_icon = ImageTk.PhotoImage(raw_icon)
                self.iconphoto(True, tk_icon)
                self._img_refs["app_icon"] = tk_icon
            except Exception:
                pass

        # Windows 10/11 Dark Title Bar via DWM
        try:
            self.update()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20 (or 19 on early Win10 builds)
            for attr in (20, 19):
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attr, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
                )
        except Exception:
            pass

    # ── Root layout ──────────────────────────────────────────────────────────

    def _build_layout(self):
        # 1. Left Sidebar
        self.sidebar_frame = tk.Frame(self, bg=SIDE_BG, width=SIDEBAR_WIDTH)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # 2. Right Workspace (Header + Viewport + Status Bar)
        self.workspace_frame = tk.Frame(self, bg=APP_BG)
        self.workspace_frame.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._build_header()
        self._build_status_bar()
        self._build_viewport()

    # ─────────────────────────────────────────────────────────────────────────
    # SIDEBAR COMPONENT (Interactive View Switcher)
    # ─────────────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sf = self.sidebar_frame

        # 1px subtle right border
        tk.Frame(sf, bg=BORDER, width=1).place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        # Top Logo Card
        logo_area = tk.Frame(sf, bg=SIDE_BG, height=84)
        logo_area.pack(fill="x")
        logo_area.pack_propagate(False)

        logo_label = tk.Label(logo_area, bg=SIDE_BG, cursor="hand2")
        logo_label.place(relx=0.5, rely=0.45, anchor="center")

        logo_path = _find_file(LOGO_FILE)
        logo_img = _get_logo(logo_path, 44)
        if logo_img:
            logo_label.config(image=logo_img)
            self._img_refs["sb_logo"] = logo_img
        else:
            logo_label.config(text="✕", font=("Segoe UI", 24, "bold"), fg=SIL)

        logo_label.bind("<Button-1>", lambda _: self._switch_tab("about"))
        Tooltip(logo_label, "XMON Corporation — Click for About Me")

        tk.Label(sf, text="XMON", font=("Segoe UI", 7, "bold"), fg=TXT_3, bg=SIDE_BG).pack()
        tk.Frame(sf, bg=BORDER_D, height=1).pack(fill="x", padx=12, pady=(6, 12))

        # Interactive Navigation Items
        nav_definitions = [
            ("exporter", "📤", "Exporter", "Main Export Dashboard"),
            ("logs",     "📋", "Logs",     "Live Log Console & Search"),
            ("settings", "⚙",  "Settings", "Preferences & Rate Limits"),
            ("about",    "👤", "About Me", "Author Profile & Portfolio"),
            ("support",  "◎",  "Support",  "Bot Setup Guide & Help"),
        ]

        self.nav_items_frame = tk.Frame(sf, bg=SIDE_BG)
        self.nav_items_frame.pack(fill="x")

        for tab_id, icon, label, tip in nav_definitions:
            self._create_nav_button(self.nav_items_frame, tab_id, icon, label, tip)

        # Flexible bottom spacer
        tk.Frame(sf, bg=SIDE_BG).pack(fill="both", expand=True)

        # Bottom Version & Brand Badge
        badge = tk.Frame(sf, bg="#0e0e0e", highlightthickness=1, highlightbackground=BORDER)
        badge.pack(fill="x", padx=8, pady=(0, 6))
        tk.Label(
            badge, text="XMON\nCorp\n© 2026",
            font=FONT_TIN, fg=TXT_3, bg="#0e0e0e", justify="center"
        ).pack(pady=6)

        ver_lbl = tk.Label(sf, text=APP_VER, font=("Segoe UI", 8, "bold"), fg=SIL_DIM, bg=SIDE_BG)
        ver_lbl.pack(pady=(0, 8))

    def _create_nav_button(self, parent, tab_id: str, icon: str, label: str, tip: str):
        outer = tk.Frame(parent, bg=SIDE_BG, cursor="hand2")
        outer.pack(fill="x", pady=2)

        # Left indicator accent strip
        accent = tk.Frame(outer, bg=SIDE_BG, width=3)
        accent.pack(side="left", fill="y")

        inner = tk.Frame(outer, bg=SIDE_BG, pady=9)
        inner.pack(fill="x", expand=True)

        icon_lbl = tk.Label(inner, text=icon, font=("Segoe UI Symbol", 13), fg=TXT_3, bg=SIDE_BG)
        icon_lbl.pack()

        txt_lbl = tk.Label(inner, text=label, font=FONT_NAV, fg=TXT_3, bg=SIDE_BG)
        txt_lbl.pack(pady=(1, 0))

        all_widgets = [outer, inner, accent, icon_lbl, txt_lbl]

        self._nav_widgets[tab_id] = {
            "outer": outer, "inner": inner, "accent": accent,
            "icon": icon_lbl, "txt": txt_lbl, "all": all_widgets
        }

        def on_click(_=None):
            self._switch_tab(tab_id)

        def on_enter(_=None):
            if self._active_tab != tab_id:
                for w in [outer, inner]:
                    w.config(bg="#141414")
                icon_lbl.config(bg="#141414", fg=TXT_2)
                txt_lbl.config(bg="#141414", fg=TXT_2)

        def on_leave(_=None):
            if self._active_tab != tab_id:
                for w in [outer, inner]:
                    w.config(bg=SIDE_BG)
                icon_lbl.config(bg=SIDE_BG, fg=TXT_3)
                txt_lbl.config(bg=SIDE_BG, fg=TXT_3)

        for w in all_widgets:
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        Tooltip(outer, tip)

    def _switch_tab(self, tab_id: str):
        self._active_tab = tab_id

        # Update sidebar visual highlighting
        for tid, d in self._nav_widgets.items():
            is_sel = (tid == tab_id)
            active_bg = "#181818" if is_sel else SIDE_BG
            fg_col = SIL_HI if is_sel else TXT_3
            d["outer"].config(bg=active_bg)
            d["inner"].config(bg=active_bg)
            d["accent"].config(bg=SIL if is_sel else SIDE_BG)
            d["icon"].config(bg=active_bg, fg=fg_col)
            d["txt"].config(bg=active_bg, fg=fg_col)

        # Switch visible viewport
        for tid, view_frame in self._views.items():
            if tid == tab_id:
                view_frame.pack(fill="both", expand=True)
            else:
                view_frame.pack_forget()

        # Update status bar breadcrumb
        tab_titles = {
            "exporter": "Ready",
            "logs": "Log Inspector",
            "settings": "Settings & Preferences",
            "about": "About Me & Developer Portfolio",
            "support": "Support & Documentation"
        }
        if not self._is_exporting:
            self._status_var.set(tab_titles.get(tab_id, "Ready"))

    # ─────────────────────────────────────────────────────────────────────────
    # HEADER COMPONENT (Canvas with Watermark & Interactive Profile Card)
    # ─────────────────────────────────────────────────────────────────────────

    def _build_header(self):
        H = 120
        self.header_canvas = tk.Canvas(self.workspace_frame, bg=HDR_BG, height=H, highlightthickness=0)
        self.header_canvas.pack(fill="x")

        # Brand title cluster
        brand_frame = tk.Frame(self.header_canvas, bg=HDR_BG)
        tk.Label(brand_frame, text=BRAND_NAME, font=("Segoe UI", 26, "bold"), fg=SIL_HI, bg=HDR_BG).pack(anchor="w")
        tk.Label(brand_frame, text="Discord Chat Exporter  ·  Official REST API v10", font=("Segoe UI", 11), fg=TXT_2, bg=HDR_BG).pack(anchor="w")
        tk.Label(brand_frame, text="🛡️ Read-Only  ·  100% In-Memory Token Safety  ·  Anti-Rate Limit", font=FONT_TIN, fg=TXT_3, bg=HDR_BG).pack(anchor="w", pady=(2, 0))

        self.header_canvas.create_window(24, H // 2, window=brand_frame, anchor="w")

        # GitHub Profile Quick Card
        gh_card = self._create_header_profile_card(self.header_canvas)
        self._gh_card_win = self.header_canvas.create_window(0, H // 2, window=gh_card, anchor="e")

        # Resize event for watermark and card repositioning
        self.header_canvas.bind("<Configure>", self._on_header_resize)

        # 1px border under header
        tk.Frame(self.workspace_frame, bg=BORDER, height=1).pack(fill="x")

    def _create_header_profile_card(self, parent):
        GB = "#0f0f0f"
        card = tk.Frame(parent, bg=BORDER, padx=1, pady=1, cursor="hand2")
        inner = tk.Frame(card, bg=GB, padx=14, pady=8)
        inner.pack(fill="x")

        row = tk.Frame(inner, bg=GB)
        row.pack()

        # Circular Avatar
        avatar_lbl = tk.Label(row, bg=GB)
        avatar_lbl.pack(side="left", padx=(0, 10))

        av_path = _find_file(AVATAR_FILE)
        av_img = _get_circle_avatar(av_path, 44)
        if av_img:
            avatar_lbl.config(image=av_img)
            self._img_refs["hdr_avatar"] = av_img
        else:
            avatar_lbl.config(text="◉", font=("Segoe UI Symbol", 20), fg=SIL_DIM)

        # Text column
        tc = tk.Frame(row, bg=GB)
        tc.pack(side="left")

        gh_row = tk.Frame(tc, bg=GB)
        gh_row.pack(anchor="w")
        tk.Label(gh_row, text="Developer", font=FONT_TIN, fg=TXT_3, bg=GB).pack(anchor="w")
        tk.Label(gh_row, text="XMON", font=("Segoe UI", 11, "bold"), fg=SIL_HI, bg=GB).pack(anchor="w")
        tk.Label(tc, text="xmon4u.github.io ↗", font=FONT_TIN, fg=SIL, bg=GB).pack(anchor="w")

        all_w = [card, inner, row, avatar_lbl, tc, gh_row] + list(tc.winfo_children())

        def on_enter(_):
            card.config(bg=BORDER_F)
            for w in [inner, row, avatar_lbl, tc, gh_row]:
                try: w.config(bg="#161616")
                except Exception: pass

        def on_leave(_):
            card.config(bg=BORDER)
            for w in [inner, row, avatar_lbl, tc, gh_row]:
                try: w.config(bg=GB)
                except Exception: pass

        def on_click(_):
            self._switch_tab("about")

        for w in all_w:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        Tooltip(card, "View About Me & Developer Portfolio")
        return card

    def _on_header_resize(self, event):
        w, h = event.width, event.height
        # Flush card to right
        self.header_canvas.coords(self._gh_card_win, w - 24, h // 2)

        # Watermark redraw
        self.header_canvas.delete("watermark")
        logo_path = _find_file(LOGO_FILE)
        if logo_path and PIL:
            sz = min(int(h * 2.3), 360)
            wm = _get_watermark(logo_path, sz, 0.10)
            if wm:
                self._img_refs["hdr_wm"] = wm
                self.header_canvas.create_image(w - sz // 3, h // 2, image=wm, anchor="center", tags="watermark")
                self.header_canvas.lower("watermark")

    # ─────────────────────────────────────────────────────────────────────────
    # STATUS BAR COMPONENT
    # ─────────────────────────────────────────────────────────────────────────

    def _build_status_bar(self):
        self.statusbar = tk.Frame(self.workspace_frame, bg="#050505", height=28)
        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(False)

        # 1px top border
        tk.Frame(self.workspace_frame, bg=BORDER, height=1).pack(fill="x", side="bottom")

        # Left status text + indicator dot
        left_box = tk.Frame(self.statusbar, bg="#050505")
        left_box.pack(side="left", padx=16, fill="y")

        self.status_dot = tk.Label(left_box, text="●", font=("Segoe UI", 9), fg=OK_COL, bg="#050505")
        self.status_dot.pack(side="left", padx=(0, 6))

        self._status_var = tk.StringVar(value="Ready")
        tk.Label(left_box, textvariable=self._status_var, font=FONT_TIN, fg=TXT_2, bg="#050505").pack(side="left")

        # Right external links
        right_box = tk.Frame(self.statusbar, bg="#050505")
        right_box.pack(side="right", padx=16, fill="y")

        web_link = tk.Label(right_box, text="xmon4u.github.io", font=FONT_TIN, fg=SIL, bg="#050505", cursor="hand2")
        web_link.pack(side="left", padx=(0, 12))
        web_link.bind("<Button-1>", lambda _: webbrowser.open(WEBSITE_URL))
        Tooltip(web_link, f"Open {WEBSITE_URL} in browser")

        gh_link = tk.Label(right_box, text="github.com/Xmon4u", font=FONT_TIN, fg=TXT_3, bg="#050505", cursor="hand2")
        gh_link.pack(side="left")
        gh_link.bind("<Button-1>", lambda _: webbrowser.open(GITHUB_URL))
        Tooltip(gh_link, f"Open {GITHUB_URL} in browser")

    # ─────────────────────────────────────────────────────────────────────────
    # VIEWPORT CONTAINER & TAB VIEWS
    # ─────────────────────────────────────────────────────────────────────────

    def _build_viewport(self):
        self.viewport_container = tk.Frame(self.workspace_frame, bg=APP_BG)
        self.viewport_container.pack(fill="both", expand=True)

        # Initialize the 5 Views
        self._views["exporter"] = self._create_exporter_view(self.viewport_container)
        self._views["logs"]     = self._create_logs_view(self.viewport_container)
        self._views["settings"] = self._create_settings_view(self.viewport_container)
        self._views["about"]    = self._create_about_view(self.viewport_container)
        self._views["support"]  = self._create_support_view(self.viewport_container)

    # ─────────────────────────────────────────────────────────────────────────
    # 1. EXPORTER VIEW (Main Dashboard)
    # ─────────────────────────────────────────────────────────────────────────

    def _create_exporter_view(self, parent) -> tk.Frame:
        # Outer scrollable wrapper to gracefully accommodate different display heights
        view_root = tk.Frame(parent, bg=APP_BG)

        canvas = tk.Canvas(view_root, bg=APP_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(view_root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=APP_BG)
        body_win = canvas.create_window((0, 0), window=body, anchor="nw")

        # Safe dynamic scrolling without overriding child text widgets
        body.bind("<Configure>", lambda _: canvas.config(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(body_win, width=e.width))

        def _on_enter_scroll(_):
            canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        def _on_leave_scroll(_):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _on_enter_scroll)
        canvas.bind("<Leave>", _on_leave_scroll)

        # ── Form Content ──
        tk.Frame(body, bg=APP_BG, height=8).pack(fill="x")

        # 1. Credentials Card
        self._build_credentials_card(body)

        # 2. Export Mode Card
        self._build_mode_card(body)

        # 3. Export Format Card
        self._build_format_card(body)

        # 4. Save Location Card
        self._build_location_card(body)

        # 5. Actions & Live Progress Card
        self._build_actions_card(body)

        # 6. Embedded Quick Log
        self._build_quick_log_card(body)

        # Bottom space
        tk.Frame(body, bg=APP_BG, height=20).pack(fill="x")

        return view_root

    def _card_wrapper(self, parent, icon: str, title: str):
        outer = tk.Frame(parent, bg=APP_BG, padx=16, pady=5)
        outer.pack(fill="x")
        border = tk.Frame(outer, bg=BORDER, padx=1, pady=1)
        border.pack(fill="x")
        card = tk.Frame(border, bg=CARD_BG, padx=18, pady=14)
        card.pack(fill="x")

        if title:
            header_row = tk.Frame(card, bg=CARD_BG)
            header_row.pack(fill="x", pady=(0, 12))
            if icon:
                tk.Label(header_row, text=icon, font=("Segoe UI Symbol", 11), fg=SIL, bg=CARD_BG).pack(side="left", padx=(0, 8))
            tk.Label(header_row, text=title, font=FONT_H2, fg=SIL_HI, bg=CARD_BG).pack(side="left")

        return card

    def _styled_entry(self, parent, show=None, textvariable=None):
        e = tk.Entry(
            parent, show=show, textvariable=textvariable,
            font=FONT_B, bg=INP_BG, fg=TXT_1,
            insertbackground=SIL_HI, relief="flat",
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=BORDER_F,
            disabledbackground=INP_BG, disabledforeground=TXT_4
        )
        e.bind("<FocusIn>",  lambda _: e.config(highlightbackground=BORDER_F))
        e.bind("<FocusOut>", lambda _: e.config(highlightbackground=BORDER))
        return e

    # ── Exporter Card: Credentials ──
    def _build_credentials_card(self, parent):
        card = self._card_wrapper(parent, "🔑", "Discord Bot Credentials")
        self.token_var = tk.StringVar()
        self.channel_var = tk.StringVar()

        # Bot Token Row
        row1 = tk.Frame(card, bg=CARD_BG)
        row1.pack(fill="x", pady=(0, 6))

        tk.Label(row1, text="Bot Token", font=FONT_B, fg=TXT_3, bg=CARD_BG, width=15, anchor="e").pack(side="left", padx=(0, 12))

        t_box = tk.Frame(row1, bg=CARD_BG)
        t_box.pack(side="left", fill="x", expand=True)

        t_border = tk.Frame(t_box, bg=BORDER, padx=1, pady=1)
        t_border.pack(fill="x")
        t_inner = tk.Frame(t_border, bg=INP_BG)
        t_inner.pack(fill="x")

        self.token_entry = tk.Entry(
            t_inner, textvariable=self.token_var, show="•",
            font=FONT_B, bg=INP_BG, fg=TXT_1,
            insertbackground=SIL_HI, relief="flat",
            highlightthickness=0
        )
        self.token_entry.pack(side="left", fill="x", expand=True, padx=10, pady=7)

        self.eye_btn = tk.Button(
            t_inner, text="👁", font=("Segoe UI Symbol", 10),
            fg=TXT_3, bg=INP_BG, activeforeground=TXT_1, activebackground=INP_BG,
            relief="flat", bd=0, cursor="hand2", padx=10, command=self._toggle_token_visibility
        )
        self.eye_btn.pack(side="right")
        Tooltip(self.eye_btn, "Toggle token visibility")

        tk.Label(t_box, text="🔒 Kept strictly in-memory — never saved, cached, or transmitted to any third-party.",
                 font=FONT_TIN, fg=TXT_3, bg=CARD_BG).pack(anchor="w", pady=(3, 0))

        # Channel ID Row
        row2 = tk.Frame(card, bg=CARD_BG)
        row2.pack(fill="x", pady=(8, 0))

        tk.Label(row2, text="Channel ID", font=FONT_B, fg=TXT_3, bg=CARD_BG, width=15, anchor="e").pack(side="left", padx=(0, 12))

        c_box = tk.Frame(row2, bg=CARD_BG)
        c_box.pack(side="left", fill="x", expand=True)

        self.channel_entry = self._styled_entry(c_box, textvariable=self.channel_var)
        self.channel_entry.pack(fill="x")

        tk.Label(c_box, text="💡 Right-click channel in Discord → Copy Channel ID (or paste the channel link).",
                 font=FONT_TIN, fg=TXT_3, bg=CARD_BG).pack(anchor="w", pady=(3, 0))

    def _toggle_token_visibility(self):
        self._show_tok = not self._show_tok
        self.token_entry.config(show="" if self._show_tok else "•")
        self.eye_btn.config(fg=TXT_1 if self._show_tok else TXT_3)

    # ── Exporter Card: Mode ──
    def _build_mode_card(self, parent):
        card = self._card_wrapper(parent, "🔍", "Export Filtering Mode")
        self.mode_var = tk.StringVar(value="all")
        self.webhook_name_var = tk.StringVar()
        self._mode_widgets = {}

        modes = [
            ("all",              "All Messages",          "Export every message sent in this channel by users, bots & webhooks."),
            ("webhook_only",     "Webhook Messages Only", "Filter and export only messages generated through Discord Webhooks."),
            ("specific_webhook", "Specific Webhook",      "Filter only messages from a specific webhook display name."),
        ]

        for val, label, desc in modes:
            self._create_mode_pill(card, val, label, desc)

        tk.Frame(card, bg=BORDER_D, height=1).pack(fill="x", pady=(12, 10))

        # Specific webhook name row
        w_row = tk.Frame(card, bg=CARD_BG)
        w_row.pack(fill="x")

        tk.Label(w_row, text="Webhook Name", font=FONT_B, fg=TXT_3, bg=CARD_BG, width=15, anchor="e").pack(side="left", padx=(0, 12))
        w_col = tk.Frame(w_row, bg=CARD_BG)
        w_col.pack(side="left", fill="x", expand=True)

        self.webhook_entry = self._styled_entry(w_col, textvariable=self.webhook_name_var)
        self.webhook_entry.pack(fill="x")

        tk.Label(w_col, text="Case-insensitive. Must match the exact name of the webhook.", font=FONT_TIN, fg=TXT_3, bg=CARD_BG).pack(anchor="w", pady=(3, 0))

        self._update_webhook_field_state()

    def _create_mode_pill(self, parent, val: str, title: str, desc: str):
        is_sel = (val == self.mode_var.get())
        bg_col = SEL_BG if is_sel else CARD_BG2

        border = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        border.pack(fill="x", pady=(0, 5))

        inner = tk.Frame(border, bg=bg_col, padx=14, pady=9, cursor="hand2")
        inner.pack(fill="x")

        top_row = tk.Frame(inner, bg=bg_col)
        top_row.pack(fill="x")

        radio_cv = tk.Canvas(top_row, width=16, height=16, bg=bg_col, highlightthickness=0)
        radio_cv.pack(side="left", padx=(0, 10))
        self._draw_radio(radio_cv, is_sel, bg_col)

        title_lbl = tk.Label(top_row, text=title, font=FONT_H3, fg=TXT_1 if is_sel else TXT_2, bg=bg_col)
        title_lbl.pack(side="left")

        desc_lbl = tk.Label(inner, text=desc, font=FONT_TIN, fg=TXT_3, bg=bg_col, anchor="w")
        desc_lbl.pack(anchor="w", pady=(3, 0))

        all_w = [border, inner, top_row, radio_cv, title_lbl, desc_lbl]

        self._mode_widgets[val] = {
            "border": border, "inner": inner, "radio": radio_cv,
            "title": title_lbl, "desc": desc_lbl, "all": all_w
        }

        def on_click(_=None):
            self.mode_var.set(val)
            self._refresh_mode_pills()
            self._update_webhook_field_state()

        def on_enter(_):
            if self.mode_var.get() != val:
                hb = "#151515"
                for w in [inner, top_row, desc_lbl]:
                    try: w.config(bg=hb)
                    except Exception: pass
                self._draw_radio(radio_cv, False, hb)

        def on_leave(_):
            if self.mode_var.get() != val:
                for w in [inner, top_row, desc_lbl]:
                    try: w.config(bg=CARD_BG2)
                    except Exception: pass
                self._draw_radio(radio_cv, False, CARD_BG2)

        for w in all_w:
            w.bind("<Button-1>", on_click)
        inner.bind("<Enter>", on_enter)
        inner.bind("<Leave>", on_leave)

    def _draw_radio(self, cv: tk.Canvas, is_sel: bool, bg: str):
        cv.config(bg=bg)
        cv.delete("all")
        cv.create_oval(1, 1, 15, 15, outline=SIL if is_sel else TXT_3, width=1.5)
        if is_sel:
            cv.create_oval(4, 4, 12, 12, fill=SIL_HI, outline="")

    def _refresh_mode_pills(self):
        sel_val = self.mode_var.get()
        for val, d in self._mode_widgets.items():
            s = (val == sel_val)
            bg = SEL_BG if s else CARD_BG2
            d["inner"].config(bg=bg)
            d["title"].config(bg=bg, fg=TXT_1 if s else TXT_2)
            d["desc"].config(bg=bg)
            self._draw_radio(d["radio"], s, bg)

    def _update_webhook_field_state(self):
        is_specific = (self.mode_var.get() == "specific_webhook")
        self.webhook_entry.config(state="normal" if is_specific else "disabled")

    # ── Exporter Card: Format ──
    def _build_format_card(self, parent):
        card = self._card_wrapper(parent, "📄", "Export Format")
        self.format_var = tk.StringVar(value=self.config_data.get("default_format", "txt"))
        self._format_widgets = {}

        formats = [
            ("txt",  "TXT",  "Formatted plain text, easy to read"),
            ("json", "JSON", "Structured JSON with attachments & embeds"),
            ("csv",  "CSV",  "Tabular spreadsheet format for Excel"),
        ]

        row = tk.Frame(card, bg=CARD_BG)
        row.pack(fill="x")

        for i, (val, label, desc) in enumerate(formats):
            col = tk.Frame(row, bg=CARD_BG)
            col.pack(side="left", fill="x", expand=True, padx=(0, 8 if i < 2 else 0))
            self._create_format_pill(col, val, label, desc)

    def _create_format_pill(self, parent, val: str, label: str, desc: str):
        is_sel = (val == self.format_var.get())
        bg_col = SEL_BG if is_sel else CARD_BG2

        border = tk.Frame(parent, bg=SIL if is_sel else BORDER, padx=1, pady=1)
        border.pack(fill="x")

        inner = tk.Frame(border, bg=bg_col, padx=12, pady=10, cursor="hand2")
        inner.pack(fill="x")

        top = tk.Frame(inner, bg=bg_col)
        top.pack(fill="x")

        cv = tk.Canvas(top, width=14, height=14, bg=bg_col, highlightthickness=0)
        cv.pack(side="left", padx=(0, 8))
        self._draw_radio_sm(cv, is_sel, bg_col)

        title_lbl = tk.Label(top, text=label, font=FONT_H3, fg=TXT_1 if is_sel else TXT_2, bg=bg_col)
        title_lbl.pack(side="left")

        desc_lbl = tk.Label(inner, text=desc, font=FONT_TIN, fg=TXT_3, bg=bg_col, anchor="w")
        desc_lbl.pack(anchor="w", pady=(3, 0))

        all_w = [border, inner, top, cv, title_lbl, desc_lbl]
        self._format_widgets[val] = {
            "border": border, "inner": inner, "cv": cv,
            "title": title_lbl, "desc": desc_lbl, "all": all_w
        }

        def on_click(_=None):
            self.format_var.set(val)
            self._refresh_format_pills()

        def on_enter(_):
            if self.format_var.get() != val:
                hb = "#151515"
                for w in [inner, top, desc_lbl]:
                    try: w.config(bg=hb)
                    except Exception: pass
                self._draw_radio_sm(cv, False, hb)

        def on_leave(_):
            if self.format_var.get() != val:
                for w in [inner, top, desc_lbl]:
                    try: w.config(bg=CARD_BG2)
                    except Exception: pass
                self._draw_radio_sm(cv, False, CARD_BG2)

        for w in all_w:
            w.bind("<Button-1>", on_click)
        inner.bind("<Enter>", on_enter)
        inner.bind("<Leave>", on_leave)

    def _draw_radio_sm(self, cv: tk.Canvas, is_sel: bool, bg: str):
        cv.config(bg=bg)
        cv.delete("all")
        cv.create_oval(1, 1, 13, 13, outline=SIL if is_sel else TXT_3, width=1.5)
        if is_sel:
            cv.create_oval(4, 4, 10, 10, fill=SIL_HI, outline="")

    def _refresh_format_pills(self):
        sel_val = self.format_var.get()
        for val, d in self._format_widgets.items():
            s = (val == sel_val)
            bg = SEL_BG if s else CARD_BG2
            d["border"].config(bg=SIL if s else BORDER)
            d["inner"].config(bg=bg)
            d["title"].config(bg=bg, fg=TXT_1 if s else TXT_2)
            d["desc"].config(bg=bg)
            self._draw_radio_sm(d["cv"], s, bg)

    # ── Exporter Card: Save Location ──
    def _build_location_card(self, parent):
        card = self._card_wrapper(parent, "📁", "Save Location")
        self.output_var = tk.StringVar(value=self.config_data.get("output_folder", os.path.expanduser("~\\Desktop")))

        row = tk.Frame(card, bg=CARD_BG)
        row.pack(fill="x")

        tk.Label(row, text="Output Directory", font=FONT_B, fg=TXT_3, bg=CARD_BG, width=15, anchor="e").pack(side="left", padx=(0, 12))

        entry = self._styled_entry(row, textvariable=self.output_var)
        entry.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(
            row, text="  Browse…  ", command=self._on_browse_output,
            font=FONT_BTN, fg=TXT_2, bg="#1a1a1a",
            activeforeground=TXT_1, activebackground="#252525",
            relief="flat", bd=0, cursor="hand2", padx=12, pady=7,
            highlightthickness=1, highlightbackground=BORDER
        )
        browse_btn.pack(side="left", padx=(8, 0))

        open_btn = tk.Button(
            row, text=" 📂 Open ", command=self._on_open_output_folder,
            font=FONT_BTN, fg=TXT_2, bg="#1a1a1a",
            activeforeground=TXT_1, activebackground="#252525",
            relief="flat", bd=0, cursor="hand2", padx=12, pady=7,
            highlightthickness=1, highlightbackground=BORDER
        )
        open_btn.pack(side="left", padx=(6, 0))

        Tooltip(browse_btn, "Select export folder")
        Tooltip(open_btn, "Open current folder in File Explorer")

    def _on_browse_output(self):
        folder = filedialog.askdirectory(title="Select Destination Folder", initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)
            self.config_data["output_folder"] = folder
            self._save_config()
            self._status_var.set(f"Destination: {folder}")

    def _on_open_output_folder(self):
        folder = self.output_var.get().strip()
        if os.path.isdir(folder):
            try:
                os.startfile(folder)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open directory:\n{e}")
        else:
            messagebox.showwarning("Directory Not Found", f"The folder does not exist:\n{folder}")

    # ── Exporter Card: Action Buttons & Progress ──
    def _build_actions_card(self, parent):
        outer = tk.Frame(parent, bg=APP_BG, padx=16, pady=6)
        outer.pack(fill="x")

        # Progress bar (smooth indeterminate during export)
        self.prog_bar = ttk.Progressbar(outer, mode="indeterminate")

        btn_row = tk.Frame(outer, bg=APP_BG)
        btn_row.pack(fill="x")

        # Start Export Button
        self.start_btn = tk.Button(
            btn_row, text="▶   Start Export", command=self._on_start_export,
            font=FONT_BTN, fg="#080808", bg=SIL,
            activeforeground="#080808", activebackground=SIL_HOV,
            relief="flat", bd=0, cursor="hand2", pady=12,
            highlightthickness=1, highlightbackground=SIL
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        # Stop Export Button
        self.stop_btn = tk.Button(
            btn_row, text="⏹   Stop Export", command=self._on_stop_export,
            font=FONT_BTN, fg=TXT_3, bg="#161616",
            activeforeground=ERR_COL, activebackground="#222222",
            relief="flat", bd=0, cursor="arrow", state="disabled", pady=12,
            highlightthickness=1, highlightbackground=BORDER
        )
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        # Clear Log Button
        self.clear_btn = tk.Button(
            btn_row, text="✕   Clear Log", command=self._on_clear_logs,
            font=FONT_BTN, fg=TXT_2, bg="#161616",
            activeforeground=TXT_1, activebackground="#222222",
            relief="flat", bd=0, cursor="hand2", pady=12,
            highlightthickness=1, highlightbackground=BORDER
        )
        self.clear_btn.pack(side="left", fill="x", expand=True)

        Tooltip(self.start_btn, "Begin extracting messages with official Discord REST API")
        Tooltip(self.stop_btn, "Safely stop the ongoing export")
        Tooltip(self.clear_btn, "Reset log output")

    # ── Exporter Card: Embedded Quick Log ──
    def _build_quick_log_card(self, parent):
        card = self._card_wrapper(parent, "📋", "Live Export Log")

        self.log_text = scrolledtext.ScrolledText(
            card, height=10, font=FONT_MON,
            bg="#040404", fg=TXT_2,
            insertbackground=SIL_HI,
            relief="flat", wrap="word",
            highlightthickness=1, highlightbackground=BORDER,
            selectbackground=BORDER, selectforeground=TXT_1
        )
        self.log_text.pack(fill="both", expand=True)

        # Style tags
        self.log_text.tag_config("info", foreground=TXT_2)
        self.log_text.tag_config("success", foreground=OK_COL)
        self.log_text.tag_config("warning", foreground=WRN_COL)
        self.log_text.tag_config("error", foreground=ERR_COL)
        self.log_text.tag_config("muted", foreground=TXT_3)

        self.log_text.config(state="normal")
        self.log_text.insert("end", "System initialized. Ready to export channel data.\n", "muted")
        self.log_text.config(state="disabled")

    # ── Logging helper ──
    def append_log(self, message: str, tag: str = "info"):
        def _write():
            # Write to embedded exporter log
            self.log_text.config(state="normal")
            self.log_text.insert("end", f"{message}\n", tag)
            self.log_text.see("end")
            self.log_text.config(state="disabled")

            # Write to full logs tab
            if hasattr(self, "full_log_text"):
                self.full_log_text.config(state="normal")
                self.full_log_text.insert("end", f"{message}\n", tag)
                if self.auto_scroll_var.get():
                    self.full_log_text.see("end")
                self.full_log_text.config(state="disabled")

        self.after(0, _write)

    def _on_clear_logs(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

        if hasattr(self, "full_log_text"):
            self.full_log_text.config(state="normal")
            self.full_log_text.delete("1.0", "end")
            self.full_log_text.config(state="disabled")

        self._status_var.set("Log cleared.")

    # ── Export Thread Execution ──
    def _on_start_export(self):
        raw_token   = self.token_var.get()
        raw_channel = self.channel_var.get()
        fmt         = self.format_var.get()
        mode        = self.mode_var.get()
        wh_name     = self.webhook_name_var.get().strip()
        out_dir     = self.output_var.get().strip()

        # Sanitize
        clean_token = sanitize_token(raw_token)
        clean_channel = sanitize_channel_id(raw_channel)

        if not clean_token:
            messagebox.showerror("Missing Token", "Please provide a valid Discord Bot Token.")
            return
        if not clean_channel:
            messagebox.showerror("Missing Channel", "Please provide a valid Channel ID or link.")
            return
        if mode == "specific_webhook" and not wh_name:
            messagebox.showerror("Missing Webhook Name", "Please enter the target Webhook Name for filtering.")
            return
        if not os.path.isdir(out_dir):
            try:
                os.makedirs(out_dir, exist_ok=True)
            except Exception:
                messagebox.showerror("Invalid Directory", f"Could not create output directory:\n{out_dir}")
                return

        # UI state transitions
        self._is_exporting = True
        self._cancel_event.clear()

        self.start_btn.config(state="disabled", text="⏳  Exporting…", cursor="watch")
        self.stop_btn.config(state="normal", fg=ERR_COL, bg="#201010", cursor="hand2")
        self.status_dot.config(fg=WRN_COL)
        self._status_var.set("Export in progress…")

        self.prog_bar.pack(fill="x", pady=(0, 8), before=self.start_btn.master)
        self.prog_bar.start(15)

        # Clear and header log
        self._on_clear_logs()
        self.append_log(f"Starting XMON Chat Exporter {APP_VER}", "info")
        self.append_log(f"Channel ID: {clean_channel} | Mode: {mode} | Format: {fmt.upper()}", "info")
        self.append_log("─" * 65, "muted")

        # Delay configuration from settings
        req_delay = float(self.config_data.get("request_delay", 0.4))

        self._export_thread = threading.Thread(
            target=self._run_export_worker,
            args=(clean_token, clean_channel, fmt, mode, wh_name, out_dir, req_delay),
            daemon=True
        )
        self._export_thread.start()

    def _on_stop_export(self):
        if self._is_exporting:
            self._cancel_event.set()
            self.append_log("Requesting export cancellation...", "warning")
            self._status_var.set("Stopping export…")
            self.stop_btn.config(state="disabled", text="Stopping…")

    def _run_export_worker(self, token, channel, fmt, mode, wh_name, out_dir, delay):
        saved_file = None
        try:
            exporter = DiscordExporter(
                bot_token=token,
                channel_id=channel,
                progress_callback=self.append_log,
                cancel_event=self._cancel_event,
                request_delay=delay
            )
            saved_file = exporter.export(
                output_path=out_dir,
                fmt=fmt,
                mode=mode,
                specific_webhook=wh_name
            )

            self.append_log("─" * 65, "muted")
            self.append_log("✅ Export completed successfully!", "success")
            self.append_log(f"File saved to: {saved_file}", "success")
            self.after(0, lambda: self._status_var.set(f"Completed: {os.path.basename(saved_file)}"))
            self.after(0, lambda: self.status_dot.config(fg=OK_COL))

            # Auto open folder if enabled in settings
            if self.config_data.get("auto_open_folder", True):
                try:
                    os.startfile(out_dir)
                except Exception:
                    pass

            self.after(0, lambda: messagebox.showinfo(
                "Export Successful",
                f"Your Discord messages have been exported!\n\nSaved to:\n{saved_file}"
            ))

        except InterruptedError as e:
            self.append_log(f"⚠️ {e}", "warning")
            self.after(0, lambda: self._status_var.set("Export cancelled."))
            self.after(0, lambda: self.status_dot.config(fg=WRN_COL))

        except PermissionError as e:
            self.append_log(f"❌ Permission Error: {e}", "error")
            self.after(0, lambda: self._status_var.set("Failed — Permission error"))
            self.after(0, lambda: self.status_dot.config(fg=ERR_COL))
            self.after(0, lambda: messagebox.showerror("Permission Error", str(e)))

        except ValueError as e:
            self.append_log(f"❌ Input Error: {e}", "error")
            self.after(0, lambda: self._status_var.set("Failed — Input error"))
            self.after(0, lambda: self.status_dot.config(fg=ERR_COL))
            self.after(0, lambda: messagebox.showerror("Input Error", str(e)))

        except ConnectionError as e:
            self.append_log(f"❌ Connection Error: {e}", "error")
            self.after(0, lambda: self._status_var.set("Failed — Connection error"))
            self.after(0, lambda: self.status_dot.config(fg=ERR_COL))
            self.after(0, lambda: messagebox.showerror("Connection Error", str(e)))

        except Exception as e:
            self.append_log(f"❌ Unexpected Error: {e}", "error")
            self.after(0, lambda: self._status_var.set("Failed — Unexpected error"))
            self.after(0, lambda: self.status_dot.config(fg=ERR_COL))
            self.after(0, lambda: messagebox.showerror("Export Error", f"An error occurred:\n\n{e}"))

        finally:
            def _reset_ui():
                self._is_exporting = False
                self.prog_bar.stop()
                self.prog_bar.pack_forget()
                self.start_btn.config(state="normal", text="▶   Start Export", cursor="hand2")
                self.stop_btn.config(state="disabled", text="⏹   Stop Export", fg=TXT_3, bg="#161616", cursor="arrow")

            self.after(0, _reset_ui)

    # ─────────────────────────────────────────────────────────────────────────
    # 2. LOGS VIEW (Full Screen Dedicated Inspector)
    # ─────────────────────────────────────────────────────────────────────────

    def _create_logs_view(self, parent) -> tk.Frame:
        view = tk.Frame(parent, bg=APP_BG)

        card = self._card_wrapper(view, "📋", "System & Export Logs Console")

        # Action Toolbar (Search / Filter, Copy, Save, Clear)
        toolbar = tk.Frame(card, bg=CARD_BG)
        toolbar.pack(fill="x", pady=(0, 10))

        # Search box
        tk.Label(toolbar, text="Filter:", font=FONT_SM, fg=TXT_3, bg=CARD_BG).pack(side="left", padx=(0, 6))
        self.log_search_var = tk.StringVar()
        s_entry = self._styled_entry(toolbar, textvariable=self.log_search_var)
        s_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        s_entry.bind("<KeyRelease>", self._on_filter_logs)

        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        cb = tk.Checkbutton(
            toolbar, text="Auto-Scroll", variable=self.auto_scroll_var,
            font=FONT_SM, fg=TXT_2, bg=CARD_BG, selectcolor="#1c1c1c",
            activebackground=CARD_BG, activeforeground=TXT_1
        )
        cb.pack(side="left", padx=(0, 10))

        # Copy button
        copy_btn = tk.Button(
            toolbar, text="📋 Copy All", command=self._copy_logs_to_clipboard,
            font=FONT_SM, fg=TXT_2, bg="#1c1c1c",
            activebackground="#252525", activeforeground=TXT_1,
            relief="flat", bd=0, cursor="hand2", padx=10, pady=4,
            highlightthickness=1, highlightbackground=BORDER
        )
        copy_btn.pack(side="left", padx=(0, 6))

        # Save to file
        save_btn = tk.Button(
            toolbar, text="💾 Save Log", command=self._save_log_to_file,
            font=FONT_SM, fg=TXT_2, bg="#1c1c1c",
            activebackground="#252525", activeforeground=TXT_1,
            relief="flat", bd=0, cursor="hand2", padx=10, pady=4,
            highlightthickness=1, highlightbackground=BORDER
        )
        save_btn.pack(side="left", padx=(0, 6))

        # Clear button
        clr_btn = tk.Button(
            toolbar, text="✕ Clear", command=self._on_clear_logs,
            font=FONT_SM, fg=TXT_2, bg="#1c1c1c",
            activebackground="#252525", activeforeground=TXT_1,
            relief="flat", bd=0, cursor="hand2", padx=10, pady=4,
            highlightthickness=1, highlightbackground=BORDER
        )
        clr_btn.pack(side="left")

        # Full Scrolled Text Box
        self.full_log_text = scrolledtext.ScrolledText(
            card, font=FONT_MON, bg="#040404", fg=TXT_2,
            insertbackground=SIL_HI, relief="flat", wrap="word",
            highlightthickness=1, highlightbackground=BORDER
        )
        self.full_log_text.pack(fill="both", expand=True)

        for tag, col in [("info", TXT_2), ("success", OK_COL), ("warning", WRN_COL), ("error", ERR_COL), ("muted", TXT_3)]:
            self.full_log_text.tag_config(tag, foreground=col)

        self.full_log_text.config(state="normal")
        self.full_log_text.insert("end", "XMON Log Console Ready.\n", "muted")
        self.full_log_text.config(state="disabled")

        return view

    def _copy_logs_to_clipboard(self):
        content = self.full_log_text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        self._status_var.set("Logs copied to clipboard!")

    def _save_log_to_file(self):
        f = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Log Output"
        )
        if f:
            try:
                with open(f, "w", encoding="utf-8") as file:
                    file.write(self.full_log_text.get("1.0", "end-1c"))
                messagebox.showinfo("Saved", f"Log saved successfully to:\n{f}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log file:\n{e}")

    def _on_filter_logs(self, _=None):
        query = self.log_search_var.get().lower().strip()
        self.full_log_text.tag_remove("match", "1.0", "end")
        if not query:
            return
        idx = "1.0"
        self.full_log_text.tag_config("match", background="#333311", foreground="#ffea75")
        while True:
            idx = self.full_log_text.search(query, idx, nocase=1, stopindex="end")
            if not idx:
                break
            lastidx = f"{idx}+{len(query)}c"
            self.full_log_text.tag_add("match", idx, lastidx)
            idx = lastidx

    # ─────────────────────────────────────────────────────────────────────────
    # 3. SETTINGS VIEW (Preferences & Configuration)
    # ─────────────────────────────────────────────────────────────────────────

    def _create_settings_view(self, parent) -> tk.Frame:
        view = tk.Frame(parent, bg=APP_BG)

        card = self._card_wrapper(view, "⚙", "Application Preferences & API Limits")

        # 1. Request Throttling (Rate Limit Protection)
        tk.Label(card, text="Discord API Throttling Delay", font=FONT_H3, fg=SIL_HI, bg=CARD_BG).pack(anchor="w", pady=(4, 2))
        tk.Label(
            card, text="Pause between 100-message batches. Prevents triggering Discord Cloudflare 429 rate limits.",
            font=FONT_TIN, fg=TXT_3, bg=CARD_BG
        ).pack(anchor="w", pady=(0, 8))

        delays = [
            ("0.2", "Turbo (0.2s)", "Fastest retrieval, use with caution on active bots"),
            ("0.4", "Standard (0.4s)", "Recommended: smooth retrieval within 5 req/sec limit"),
            ("0.8", "Safe (0.8s)", "Conservative: highly stable for massive message archives"),
            ("1.2", "Ultra-Safe (1.2s)", "Zero risk: for servers with strict bot oversight")
        ]

        self.delay_var = tk.StringVar(value=str(self.config_data.get("request_delay", 0.4)))
        d_frame = tk.Frame(card, bg=CARD_BG)
        d_frame.pack(fill="x", pady=(0, 16))

        for val, name, desc in delays:
            rb = tk.Radiobutton(
                d_frame, text=f"{name} — {desc}", value=val, variable=self.delay_var,
                font=FONT_SM, fg=TXT_2, bg=CARD_BG, selectcolor="#1c1c1c",
                activebackground=CARD_BG, activeforeground=TXT_1
            )
            rb.pack(anchor="w", pady=3)

        tk.Frame(card, bg=BORDER_D, height=1).pack(fill="x", pady=10)

        # 2. Automation Options
        tk.Label(card, text="Export Automation", font=FONT_H3, fg=SIL_HI, bg=CARD_BG).pack(anchor="w", pady=(4, 6))

        self.auto_open_var = tk.BooleanVar(value=self.config_data.get("auto_open_folder", True))
        cb = tk.Checkbutton(
            card, text="Automatically open destination folder in File Explorer when export finishes",
            variable=self.auto_open_var, font=FONT_B, fg=TXT_2, bg=CARD_BG,
            selectcolor="#1c1c1c", activebackground=CARD_BG, activeforeground=TXT_1
        )
        cb.pack(anchor="w", pady=4)

        tk.Frame(card, bg=BORDER_D, height=1).pack(fill="x", pady=14)

        # Save Settings Button
        save_btn = tk.Button(
            card, text="💾   Save Preferences", command=self._save_settings_action,
            font=FONT_BTN, fg="#080808", bg=SIL,
            activeforeground="#080808", activebackground=SIL_HOV,
            relief="flat", bd=0, cursor="hand2", padx=20, pady=10,
            highlightthickness=1, highlightbackground=SIL
        )
        save_btn.pack(anchor="w")

        return view

    def _save_settings_action(self):
        try:
            self.config_data["request_delay"] = float(self.delay_var.get())
            self.config_data["auto_open_folder"] = bool(self.auto_open_var.get())
            self._save_config()
            self._status_var.set("Preferences saved successfully.")
            messagebox.showinfo("Preferences Saved", "Your settings have been saved and applied.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save settings:\n{e}")

    # ─────────────────────────────────────────────────────────────────────────
    # 4. ABOUT & ABOUT ME VIEW (Author Profile & Portfolio)
    # ─────────────────────────────────────────────────────────────────────────

    def _create_about_view(self, parent) -> tk.Frame:
        view_root = tk.Frame(parent, bg=APP_BG)

        canvas = tk.Canvas(view_root, bg=APP_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(view_root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=APP_BG)
        body_win = canvas.create_window((0, 0), window=body, anchor="nw")

        body.bind("<Configure>", lambda _: canvas.config(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(body_win, width=e.width))

        def _on_enter_scroll(_):
            canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        def _on_leave_scroll(_):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _on_enter_scroll)
        canvas.bind("<Leave>", _on_leave_scroll)

        tk.Frame(body, bg=APP_BG, height=10).pack(fill="x")

        # ── HERO DEVELOPER SHOWCASE CARD ──
        dev_card = self._card_wrapper(body, "👤", "About Me  ·  Lead Developer & Creator")

        hero_row = tk.Frame(dev_card, bg=CARD_BG)
        hero_row.pack(fill="x", pady=(6, 12))

        # Avatar Container with Silver Ring
        av_border = tk.Frame(hero_row, bg=BORDER_F, padx=2, pady=2)
        av_border.pack(side="left", padx=(0, 18), anchor="n")

        av_lbl = tk.Label(av_border, bg="#0e0e0e")
        av_lbl.pack()

        av_path = _find_file(AVATAR_FILE)
        av_img = _get_circle_avatar(av_path, 80)
        if av_img:
            av_lbl.config(image=av_img)
            self._img_refs["about_avatar"] = av_img
        else:
            av_lbl.config(text="◉", font=("Segoe UI", 36), fg=SIL)

        # Developer Bio Details
        bio_col = tk.Frame(hero_row, bg=CARD_BG)
        bio_col.pack(side="left", fill="x", expand=True)

        tk.Label(bio_col, text="XMON", font=("Segoe UI", 18, "bold"), fg=SIL_HI, bg=CARD_BG).pack(anchor="w")
        tk.Label(bio_col, text="Software Engineer & Automation Architect", font=("Segoe UI", 11), fg=TXT_2, bg=CARD_BG).pack(anchor="w")
        tk.Label(bio_col, text="Founder of XMON Corporation  |  GitHub: @Xmon4u", font=FONT_SM, fg=TXT_3, bg=CARD_BG).pack(anchor="w", pady=(2, 6))

        bio_text = (
            "Specialized in high-performance automation software, Discord ecosystem tooling, "
            "and secure desktop engineering. Dedicated to crafting pixel-perfect, clean, "
            "and robust tools that respect user privacy and security."
        )
        tk.Label(bio_col, text=bio_text, font=FONT_SM, fg=TXT_2, bg=CARD_BG, wraplength=520, justify="left").pack(anchor="w")

        tk.Frame(dev_card, bg=BORDER_D, height=1).pack(fill="x", pady=12)

        # ── OFFICIAL PORTFOLIO & WEBPAGE SECTION (Prominent Clickable Requirement) ──
        web_box = tk.Frame(dev_card, bg="#0d1117", highlightthickness=1, highlightbackground=BORDER_F, padx=16, pady=12)
        web_box.pack(fill="x", pady=(0, 10))

        web_top = tk.Frame(web_box, bg="#0d1117")
        web_top.pack(fill="x")

        tk.Label(web_top, text="🌐 Official Portfolio & Website", font=FONT_H3, fg=SIL_HI, bg="#0d1117").pack(side="left")

        # Interactive Link Button & Copy Helper
        actions_row = tk.Frame(web_box, bg="#0d1117")
        actions_row.pack(fill="x", pady=(8, 0))

        url_badge = tk.Label(
            actions_row, text=f"  {WEBSITE_URL}  ",
            font=("Segoe UI", 10, "bold"), fg="#79c0ff", bg="#161b22",
            relief="flat", cursor="hand2", padx=10, pady=7,
            highlightthickness=1, highlightbackground="#30363d"
        )
        url_badge.pack(side="left", padx=(0, 10))
        url_badge.bind("<Button-1>", lambda _: webbrowser.open(WEBSITE_URL))
        Tooltip(url_badge, f"Click to open {WEBSITE_URL} in your browser")

        visit_btn = tk.Button(
            actions_row, text="  Open Portfolio ↗  ", command=lambda: webbrowser.open(WEBSITE_URL),
            font=FONT_BTN, fg="#080808", bg=SIL,
            activeforeground="#080808", activebackground=SIL_HOV,
            relief="flat", bd=0, cursor="hand2", padx=12, pady=7
        )
        visit_btn.pack(side="left", padx=(0, 8))

        copy_url_btn = tk.Button(
            actions_row, text="📋 Copy Link", command=lambda: self._copy_to_clip(WEBSITE_URL, "Website URL copied!"),
            font=FONT_BTN, fg=TXT_2, bg="#21262d",
            activeforeground=TXT_1, activebackground="#30363d",
            relief="flat", bd=0, cursor="hand2", padx=12, pady=7,
            highlightthickness=1, highlightbackground="#30363d"
        )
        copy_url_btn.pack(side="left", padx=(0, 8))

        gh_btn = tk.Button(
            actions_row, text="  GitHub Profile ↗  ", command=lambda: webbrowser.open(GITHUB_URL),
            font=FONT_BTN, fg=TXT_2, bg="#21262d",
            activeforeground=TXT_1, activebackground="#30363d",
            relief="flat", bd=0, cursor="hand2", padx=12, pady=7,
            highlightthickness=1, highlightbackground="#30363d"
        )
        gh_btn.pack(side="left")

        # ── SYSTEM & ENVIRONMENT SPECS CARD ──
        sys_card = self._card_wrapper(body, "💻", "Application & Environment Specs")

        specs = [
            ("Application Version", f"{APP_VER} (GitHub Ready Final Release)"),
            ("Discord API Protocol", "Discord REST API v10 (Official Bot Gateway)"),
            ("Python Runtime", f"Python {platform.python_version()} ({platform.architecture()[0]})"),
            ("Operating System", f"{platform.system()} {platform.release()} (Build {platform.version()})"),
            ("Graphics & UI Engine", f"Tkinter {tk.TkVersion} with Pillow {Image.__version__ if PIL else 'Fallback'}")
        ]

        for label, val in specs:
            r = tk.Frame(sys_card, bg=CARD_BG)
            r.pack(fill="x", pady=2)
            tk.Label(r, text=label, font=FONT_SM, fg=TXT_3, bg=CARD_BG, width=22, anchor="w").pack(side="left")
            tk.Label(r, text=val, font=FONT_SM, fg=TXT_1, bg=CARD_BG, anchor="w").pack(side="left")

        # ── PRIVACY & SECURITY CERTIFICATION ──
        sec_card = self._card_wrapper(body, "🛡️", "Security & Compliance Guarantees")

        points = [
            "✅ 100% In-Memory Security: Your bot token is never saved to disk, registry, or config files.",
            "✅ Zero Data Transmission: No telemetry, analytics, or external server calls are ever performed.",
            "✅ Read-Only Operation: The app strictly uses HTTP GET requests; it can never send or modify messages.",
            "✅ Official Discord API: Fully compliant with Discord Terms of Service (no self-botting)."
        ]
        for pt in points:
            tk.Label(sec_card, text=pt, font=FONT_SM, fg=TXT_2, bg=CARD_BG, anchor="w").pack(anchor="w", pady=2)

        tk.Frame(body, bg=APP_BG, height=20).pack(fill="x")
        return view_root

    def _copy_to_clip(self, text: str, feedback: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self._status_var.set(feedback)

    # ─────────────────────────────────────────────────────────────────────────
    # 5. SUPPORT & TROUBLESHOOTING VIEW
    # ─────────────────────────────────────────────────────────────────────────

    def _create_support_view(self, parent) -> tk.Frame:
        view_root = tk.Frame(parent, bg=APP_BG)

        canvas = tk.Canvas(view_root, bg=APP_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(view_root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=APP_BG)
        body_win = canvas.create_window((0, 0), window=body, anchor="nw")

        body.bind("<Configure>", lambda _: canvas.config(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(body_win, width=e.width))

        def _on_enter_scroll(_):
            canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        def _on_leave_scroll(_):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _on_enter_scroll)
        canvas.bind("<Leave>", _on_leave_scroll)

        tk.Frame(body, bg=APP_BG, height=10).pack(fill="x")

        # ── Setup Tutorial Card ──
        card = self._card_wrapper(body, "🚀", "Quick Start: Discord Bot Setup")

        steps = [
            ("Step 1", "Create Bot Application", "Go to Discord Developer Portal → 'New Application' → Name it (e.g. XMON Exporter)."),
            ("Step 2", "Enable Message Content Intent", "Under 'Bot' tab → Privileged Gateway Intents → Toggle 'Message Content Intent' ON."),
            ("Step 3", "Copy Bot Token", "Under 'Bot' tab → Click 'Reset Token' → Copy the token string."),
            ("Step 4", "Invite Bot to Server", "Under 'OAuth2' → 'URL Generator' → check 'bot' scope → permissions: 'Read Messages' & 'Read Message History' → Authorize in server."),
            ("Step 5", "Copy Channel ID", "Enable Developer Mode in Discord Settings → Right-click the channel → 'Copy Channel ID'.")
        ]

        for s_num, title, desc in steps:
            r = tk.Frame(card, bg=CARD_BG)
            r.pack(fill="x", pady=4)
            tk.Label(r, text=f"[{s_num}]", font=FONT_H3, fg=SIL, bg=CARD_BG, width=8, anchor="w").pack(side="left")
            tk.Label(r, text=f"{title}: ", font=FONT_H3, fg=TXT_1, bg=CARD_BG).pack(side="left")
            tk.Label(r, text=desc, font=FONT_SM, fg=TXT_2, bg=CARD_BG, wraplength=480, justify="left").pack(side="left")

        # Dev Portal launcher button
        dev_btn = tk.Button(
            card, text="  🌐 Open Discord Developer Portal ↗  ",
            command=lambda: webbrowser.open(DISCORD_DEV),
            font=FONT_BTN, fg="#080808", bg=SIL,
            activeforeground="#080808", activebackground=SIL_HOV,
            relief="flat", bd=0, cursor="hand2", padx=16, pady=8
        )
        dev_btn.pack(anchor="w", pady=(12, 0))

        # ── Error Dictionary Card ──
        err_card = self._card_wrapper(body, "❓", "Troubleshooting Common Errors")

        troubleshoot = [
            ("401 Unauthorized", "The bot token entered is invalid. Ensure you copied the full token without extra quotes or spaces."),
            ("403 Forbidden", "Bot lacks 'View Channels' or 'Read Message History' in that channel's server permission role settings."),
            ("404 Not Found", "Channel ID doesn't exist or bot is not inside the server containing that channel."),
            ("429 Too Many Requests", "Discord temporary rate limit. XMON automatically pauses and waits for the backoff timer to expire.")
        ]

        for code, fix in troubleshoot:
            r = tk.Frame(err_card, bg=CARD_BG)
            r.pack(fill="x", pady=4)
            tk.Label(r, text=code, font=FONT_H3, fg=WRN_COL, bg=CARD_BG, width=20, anchor="w").pack(side="left")
            tk.Label(r, text=fix, font=FONT_SM, fg=TXT_2, bg=CARD_BG, wraplength=520, justify="left").pack(side="left")

        tk.Frame(body, bg=APP_BG, height=20).pack(fill="x")
        return view_root


# ─────────────────────────────────────────────────────────────────────────────
# Application Entrypoint
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = XMONApp()
    app.mainloop()
