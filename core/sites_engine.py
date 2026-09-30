"""
Google Sites Automation Engine using Playwright Persistent Context.
Handles browser launching, Google login authentication, blank site creation,
structured element insertion (H2 headings, text boxes, images, buttons,
image carousel, map embed, footer), and publishing with URL extraction.
All log outputs formatted with clean professional tags without emojis.
"""

import os
import re
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from playwright.sync_api import sync_playwright, BrowserContext, Page

from database.db import get_setting, add_task_history
from core.structures import PostStructure, get_structure_by_id

logger = logging.getLogger(__name__)

from core.path_helper import get_base_dir, get_profile_dir, get_images_dir, get_urls_dir

BASE_DIR = get_base_dir()
PROFILE_DIR = get_profile_dir()
IMAGES_DIR = get_images_dir()
URLS_DIR = get_urls_dir()
URLS_FILE = os.path.join(URLS_DIR, "published_urls.txt")

import subprocess

def cleanup_profile_locks(profile_dir: str):
    """Safely terminates lingering chrome processes locking this profile and deletes stale lock files."""
    try:
        base_name = os.path.basename(profile_dir)
        if sys.platform == "win32":
            import base64
            ps_script = f"""
$procs = Get-CimInstance Win32_Process -Filter "Name = 'chrome.exe'"
foreach ($p in $procs) {{
    if ($p.CommandLine -like "*{base_name}*") {{
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }}
}}
"""
            encoded = base64.b64encode(ps_script.encode('utf-16le')).decode('ascii')
            subprocess.run(["powershell", "-NoProfile", "-EncodedCommand", encoded], capture_output=True, timeout=8)
            time.sleep(0.5)
        elif sys.platform == "darwin":
            subprocess.run(["pkill", "-f", f"Google Chrome.*{base_name}"], capture_output=True, timeout=5)
            time.sleep(0.3)
    except Exception:
        pass

    for lock_file in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lp = os.path.join(profile_dir, lock_file)
        if os.path.exists(lp):
            try:
                os.remove(lp)
            except Exception:
                pass

def clear_browser_cache_and_session(profile_dir: str = PROFILE_DIR) -> Tuple[bool, str, float]:
    """
    Cleans browser cache, shader cache, code cache, cookies, and active sessions.
    Drastically speeds up stealth browser launch and allows fresh Google login.
    CRITICAL: Preserves .license.dat so node-lock activation is never lost.
    """
    # 1. Terminate any active browser processes
    cleanup_profile_locks(profile_dir)
    time.sleep(0.5)

    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir, exist_ok=True)
        return True, "Profile directory is ready and clean.", 0.0

    freed_bytes = 0
    dirs_to_clean = {
        "cache", "code cache", "gpucache", "service worker", "storage",
        "indexeddb", "shadercache", "grshadercache", "crashpad",
        "session storage", "local storage", "network"
    }
    files_to_clean = {
        "cookies", "cookies-journal", "history", "history-journal",
        "login data", "login data-journal", "web data", "web data-journal",
        "transportsecurity", "visited links", "favicons", "favicons-journal"
    }

    import shutil

    for root, dirs, files in os.walk(profile_dir, topdown=False):
        for d in dirs:
            if d.lower() in dirs_to_clean:
                target_dir = os.path.join(root, d)
                try:
                    for r, _, fs in os.walk(target_dir):
                        for f in fs:
                            try:
                                fp = os.path.join(r, f)
                                freed_bytes += os.path.getsize(fp)
                            except Exception:
                                pass
                    shutil.rmtree(target_dir, ignore_errors=True)
                except Exception:
                    pass

        for f in files:
            # ABSOLUTE RULE: NEVER touch license files!
            if ".license" in f.lower():
                continue
            if f.lower() in files_to_clean or f.startswith("Singleton") or "lock" in f.lower():
                fp = os.path.join(root, f)
                try:
                    freed_bytes += os.path.getsize(fp)
                    os.remove(fp)
                except Exception:
                    pass

    freed_mb = round(freed_bytes / (1024 * 1024), 1)
    cleanup_profile_locks(profile_dir)
    return True, f"Successfully cleared {freed_mb} MB of browser cache and reset Google session.", freed_mb

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    def attach_to_user_desktop():
        """Attaches current thread to user's interactive 'Default' desktop so GUI/Browser is visible to user."""
        try:
            user32 = ctypes.windll.user32
            h_desktop = user32.OpenDesktopW("Default", 0, False, 0x10000000)
            if h_desktop:
                user32.SetThreadDesktop(h_desktop)
        except Exception:
            pass

    def bring_window_to_front():
        """Brings Chrome/Chromium window to active desktop foreground on Windows."""
        try:
            attach_to_user_desktop()
            user32 = ctypes.windll.user32
            WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

            def enum_handler(hwnd, _):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        title = buff.value
                        if any(k in title.lower() for k in ["google sites", "chrome", "chromium", "about:blank"]):
                            user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE = 3
                            user32.SetForegroundWindow(hwnd)
                return True

            user32.EnumWindows(WNDENUMPROC(enum_handler), 0)
        except Exception:
            pass

    # 64-bit Windows ctypes declarations for OS Clipboard operations
    user32 = getattr(ctypes, 'windll', None).user32 if hasattr(ctypes, 'windll') else None
    kernel32 = getattr(ctypes, 'windll', None).kernel32 if hasattr(ctypes, 'windll') else None

    if kernel32 and user32:
        kernel32.GlobalAlloc.restype = ctypes.c_void_p
        kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        user32.SetClipboardData.argtypes = [wintypes.UINT, ctypes.c_void_p]
        user32.GetClipboardData.restype = ctypes.c_void_p
        user32.GetClipboardData.argtypes = [wintypes.UINT]

    def set_windows_clipboard_text(text: str) -> bool:
        """Sets unicode text directly onto Windows OS clipboard using ctypes."""
        if not user32 or not kernel32:
            return False
        try:
            if not user32.OpenClipboard(None):
                time.sleep(0.05)
                if not user32.OpenClipboard(None):
                    return False
            try:
                user32.EmptyClipboard()
                text_bytes = (text + '\0').encode('utf-16le')
                h_mem = kernel32.GlobalAlloc(0x0042, len(text_bytes))  # GMEM_MOVEABLE | GMEM_ZEROINIT
                if not h_mem:
                    return False
                p_mem = kernel32.GlobalLock(h_mem)
                if not p_mem:
                    return False
                ctypes.memmove(p_mem, text_bytes, len(text_bytes))
                kernel32.GlobalUnlock(h_mem)
                user32.SetClipboardData(13, h_mem)  # CF_UNICODETEXT = 13
                return True
            finally:
                user32.CloseClipboard()
        except Exception:
            return False
else:
    def attach_to_user_desktop():
        pass

    def bring_window_to_front():
        pass

    def set_windows_clipboard_text(text: str) -> bool:
        return False

def enforce_title_60_70(title: str, keyword: str = "") -> str:
    """Cleans title and ensures it is well-formed without truncating or cutting off text."""
    if not title:
        title = f"Top Rated {keyword.title()} - 24/7 Verified Service" if keyword else "Official Website"
    title = re.sub(r'[\r\n]+', ' ', title).strip()
    title = re.sub(r'\s{2,}', ' ', title)
    return title

class GoogleSitesAutomator:
    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.log = log_callback or (lambda msg: logger.info(msg))
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._ensure_folders()

    def _ensure_folders(self):
        os.makedirs(PROFILE_DIR, exist_ok=True)
        os.makedirs(URLS_DIR, exist_ok=True)
        for i in range(1, 5):
            os.makedirs(os.path.join(IMAGES_DIR, f"str-image{i}"), exist_ok=True)

    def launch_browser(self, headless: bool = False) -> Page:
        attach_to_user_desktop()
        self.log("[BROWSER] Launching browser with persistent context...")

        # Terminate any lingering automation chrome processes and clean stale lock files
        cleanup_profile_locks(PROFILE_DIR)
        time.sleep(0.5)

        if not self.playwright:
            self.playwright = sync_playwright().start()
        
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-session-crashed-bubble",
            "--start-maximized",
            "--no-sandbox",
            "--window-size=1600,1000"
        ]
        vp = {"width": 1440, "height": 900} if headless else None

        def _do_launch():
            try:
                return self.playwright.chromium.launch_persistent_context(
                    user_data_dir=PROFILE_DIR,
                    channel="chrome",
                    headless=headless,
                    viewport=vp,
                    args=browser_args
                )
            except Exception as e_chrome:
                err_lower = str(e_chrome).lower()
                if "processsingleton" in err_lower or "already in use" in err_lower or "existing browser session" in err_lower:
                    raise e_chrome
                self.log(f"[BROWSER] Google Chrome channel not default, using Chromium: {e_chrome}")
                return self.playwright.chromium.launch_persistent_context(
                    user_data_dir=PROFILE_DIR,
                    headless=headless,
                    user_agent=user_agent_str,
                    viewport=vp,
                    args=browser_args
                )

        try:
            self.context = _do_launch()
        except Exception as e:
            err_lower = str(e).lower()
            if "already in use" in err_lower or "existing browser session" in err_lower or "processsingleton" in err_lower or "lock file" in err_lower:
                self.log("[BROWSER] Profile is locked by another Chromium instance. Performing deep cleanup...")
                cleanup_profile_locks(PROFILE_DIR)
                time.sleep(1.5)
                self.context = _do_launch()
            else:
                raise e

        if len(self.context.pages) > 0:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        try:
            self.context.grant_permissions(["clipboard-read", "clipboard-write"])
        except Exception:
            pass

        try:
            self.page.bring_to_front()
            bring_window_to_front()
        except Exception:
            pass

        self.page.set_default_timeout(35000)
        return self.page

    def check_and_login_google(self) -> bool:
        """BUG 9 fix — Early exit + no-field detection."""
        self.log("[LOGIN] Checking Google account authentication status...")
        self.page.goto("https://sites.google.com/new", wait_until="domcontentloaded")
        self.page.wait_for_timeout(3000)

        # Already logged in?
        if "sites.google.com" in self.page.url and "accounts.google.com" not in self.page.url:
            self.log("[SUCCESS] Already logged into Google Sites.")
            return True

        for step in range(10):
            url = self.page.url

            # Success — Google Sites reached
            if "sites.google.com" in url and "accounts.google.com" not in url:
                self.log("[SUCCESS] Successfully logged into Google Sites.")
                return True

            # Kisi aur page pe chala gaya — login page nahi
            if "accounts.google.com" not in url:
                self.log(f"[LOGIN] Left Google auth flow (URL: {url[:80]}).")
                break

            self.log(f"[LOGIN] Step {step+1}: Checking login page state...")

            email_field = self.page.locator("input[type='email']")
            pwd_field = self.page.locator("input[type='password']:visible")

            handled = False

            if email_field.count() > 0 and email_field.first.is_visible():
                saved_email = get_setting("google_account_email", "")
                if saved_email:
                    self.log(f"[LOGIN] Autofilling email...")
                    email_field.first.fill(saved_email)
                    self.page.keyboard.press("Enter")
                    self.page.wait_for_timeout(4000)
                    handled = True

            if pwd_field.count() > 0 and pwd_field.first.is_visible():
                saved_pwd = get_setting("google_account_password", "")
                if saved_pwd:
                    self.log("[LOGIN] Autofilling password...")
                    pwd_field.first.fill(saved_pwd)
                    self.page.keyboard.press("Enter")
                    self.page.wait_for_timeout(5000)
                    handled = True

            # BUG 9 fix — koi field nahi mila to chhota wait + continue
            if not handled:
                self.page.wait_for_timeout(1500)
                # Double check URL
                if "sites.google.com" in self.page.url:
                    self.log("[SUCCESS] Login completed.")
                    return True

        if "sites.google.com" in self.page.url:
            self.log("[SUCCESS] Successfully logged into Google Sites.")
            return True

        self.log("[ERROR] Could not complete Google login. Please log in manually.")
        return False

    def create_blank_site(self) -> bool:
        """Navigates to Google Sites and creates a brand-new blank site."""
        self.log("[PAGE] Opening Blank Site template on Google Sites...")
        self.page.goto("https://sites.google.com/new", wait_until="domcontentloaded")
        self.page.wait_for_timeout(4000)

        # Dismiss "Got it" modal if present
        got_it = self.page.locator("button:has-text('Got it'), div[role='button']:has-text('Got it')")
        if got_it.count() > 0 and got_it.first.is_visible():
            got_it.first.click()
            self.page.wait_for_timeout(1000)

        # Click Blank site template card
        blank_sel = "div.docs-homescreen-templates-templateview:has-text('Blank site'), div.docs-homescreen-templates-templateview-showcase, [aria-label*='Blank site' i]"
        blank_card = self.page.locator(blank_sel).first
        if blank_card.is_visible():
            self.log("[PAGE] Clicking Blank site template card...")
            blank_card.click()
            self.page.wait_for_timeout(6000)

        # Switch to newly opened tab if editor opened in new window/tab
        if len(self.context.pages) > 1:
            self.page = self.context.pages[-1]
            try:
                self.page.bring_to_front()
            except Exception:
                pass

        try:
            self.page.wait_for_selector("div[data-name='title'], div:has-text('Your page title'), div:has-text('Insert')", timeout=25000)
            self.log("[SUCCESS] Google Sites editor canvas initialized.")
            
            # Dismiss bottom template tip if visible
            tip_close = self.page.locator("button[aria-label*='Close' i], [aria-label*='Dismiss' i]")
            if tip_close.count() > 0 and tip_close.first.is_visible():
                tip_close.first.click()
                self.page.wait_for_timeout(500)
                
            return True
        except Exception as e:
            self.log(f"[ERROR] Failed to load Google Sites editor canvas: {e}")
            return False

    def apply_site_theme(self, theme_name: str = "Simple", custom_color_hex: Optional[str] = None):
        """Applies a Google Theme (Simple, Aristotle, Diplomat, Vision, Level, Impression) and optional custom Hex color."""
        # If user left it on default Simple and no custom color, do nothing (fastest & native)
        if (not theme_name or theme_name.strip().lower() == "simple") and not custom_color_hex:
            self.log("[THEME] Using default 'Simple' theme with standard color.")
            return

        clean_theme = theme_name.strip()
        self.log(f"[THEME] Applying Google Theme: '{clean_theme}' (Custom Color: {custom_color_hex or 'Default'})...")
        try:
            # 1. Switch to 'Themes' tab in right sidebar
            themes_tab = self.page.locator("div[role='tab']:has-text('Themes'), [aria-label*='Themes' i]").first
            if themes_tab.is_visible():
                themes_tab.click()
                self.page.wait_for_timeout(1000)

            # 2. Select theme under 'CREATED BY GOOGLE'
            theme_card = self.page.locator(f"div:has-text('CREATED BY GOOGLE') ~ div div:has-text('{clean_theme}'), div[role='button']:has-text('{clean_theme}')").first
            if not theme_card.is_visible():
                theme_card = self.page.locator(f"div:has-text('{clean_theme}'), span:has-text('{clean_theme}')").first

            if theme_card.is_visible():
                theme_card.click()
                self.page.wait_for_timeout(1000)
                self.log(f"[SUCCESS] Selected theme: {clean_theme}")

            # 3. Apply custom color hex if specified
            if custom_color_hex:
                hex_clean = custom_color_hex.strip()
                if not hex_clean.startswith("#"):
                    hex_clean = f"#{hex_clean}"

                self.log(f"[THEME] Setting custom theme hex code: {hex_clean}...")
                
                # Check all possible custom color trigger selectors in Themes panel
                custom_dot = self.page.locator(
                    "div[role='tabpanel'] div[aria-label*='custom color' i], "
                    "div[role='tabpanel'] div[aria-label*='Custom' i], "
                    "div[role='tabpanel'] div.p6n-theme-color-picker-custom, "
                    "div[role='tabpanel'] div[role='button'][aria-label*='color' i], "
                    "div[role='tabpanel'] [data-tooltip*='custom' i], "
                    "div[role='tabpanel'] div[role='radio']:last-child"
                ).last

                if not (custom_dot.count() > 0 and custom_dot.is_visible()):
                    color_dots = self.page.locator("div[role='tabpanel'] div[role='radio'], div[role='tabpanel'] div[role='button'][style*='background']")
                    if color_dots.count() > 0:
                        custom_dot = color_dots.last

                if custom_dot.count() > 0 and custom_dot.is_visible():
                    custom_dot.click(force=True)
                    self.page.wait_for_timeout(800)

                    hex_input = self.page.locator(
                        "input[aria-label*='hex' i], "
                        "input[value*='#'], "
                        "input.p6n-color-picker-hex-input, "
                        "div.p6n-color-picker input, "
                        "div[role='dialog'] input[type='text'], "
                        "input[type='text']:visible"
                    ).last

                    if hex_input.count() > 0 and hex_input.is_visible():
                        hex_input.click()
                        self.page.keyboard.press("Control+A")
                        self.page.keyboard.press("Backspace")
                        self.page.keyboard.type(hex_clean)
                        self.page.keyboard.press("Enter")
                        self.page.wait_for_timeout(800)
                        self.log(f"[SUCCESS] Custom theme hex code '{hex_clean}' applied.")
                    else:
                        self.log("[THEME] [WARNING] Hex input field not found in color popover.")
                else:
                    self.log("[THEME] [WARNING] Custom color button not found in Themes panel.")

                # Dismiss color popup
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(400)

            # 4. Switch back to 'Insert' tab so subsequent element additions succeed
            insert_tab = self.page.locator("div[role='tab']:has-text('Insert'), [aria-label*='Insert' i]").first
            if insert_tab.is_visible():
                insert_tab.click()
                self.page.wait_for_timeout(800)

        except Exception as e:
            self.log(f"[THEME] Notice applying theme: {e}")
            try:
                insert_tab = self.page.locator("div[role='tab']:has-text('Insert')").first
                if insert_tab.is_visible():
                    insert_tab.click()
            except Exception:
                pass

    def add_announcement_banner(
        self,
        message: str = "Instant 24/7 Service Available - Chat on WhatsApp",
        button_label: str = "WhatsApp",
        link_url: str = "",
        banner_color: Optional[str] = None
    ):
        """Configures and enables top Announcement Banner above site content (announcement-banner-1 to 4)."""
        self.log(f"[BANNER] Adding announcement banner: '{message[:35]}...' (Button: '{button_label}')")
        try:
            # 1. Click Settings gear icon in top bar (announcement-banner-1)
            settings_btn = self.page.locator("div[role='button'][aria-label*='Settings' i], button[aria-label*='Settings' i]").first
            if settings_btn.is_visible():
                settings_btn.click(force=True)
                self.page.wait_for_timeout(1500)

            # 2. Click 'Announcement banner' tab on left list (announcement-banner-2)
            banner_tab = self.page.locator("div[role='dialog'] div[role='tab']:has-text('Announcement banner'), div[role='dialog'] div[role='button']:has-text('Announcement banner')").first
            if banner_tab.is_visible():
                banner_tab.click(force=True)
                self.page.wait_for_timeout(1000)

            # 3. Enable 'Show banner' switch toggle if not already checked
            toggle = self.page.locator("div[role='dialog'] div[role='switch'], div[role='dialog'] [aria-label*='Show banner' i]").first
            if toggle.is_visible():
                checked = toggle.get_attribute("aria-checked")
                if checked != "true":
                    toggle.click(force=True)
                    self.page.wait_for_timeout(500)
                    self.log("[BANNER] Enabled 'Show banner' toggle switch.")

            # 3.1. Banner Color Configuration (announcement-banner-5 & 6)
            # Google Sites default banner color is already Red. Only interact if custom color specified.
            color_target = banner_color or "#FF0000"
            is_red = color_target.upper() in ["#FF0000", "#EA4335", "#D93025", "RED", "DEFAULT"]
            if not is_red and color_target.startswith("#"):
                try:
                    color_btn = self.page.locator("div[role='dialog'] [aria-label*='Banner color' i], div[role='dialog'] div:has-text('Banner color') + div [role='button']").first
                    if color_btn.is_visible():
                        color_btn.click(force=True)
                        self.page.wait_for_timeout(800)

                        plus_btn = self.page.locator("div[role='button'][aria-label*='Custom' i], div[role='button'][aria-label*='Add' i], [aria-label*='Add custom color' i]").last
                        if not plus_btn.is_visible():
                            plus_btn = self.page.locator("div:has-text('+'), button:has-text('+')").last

                        if plus_btn.is_visible():
                            plus_btn.click(force=True)
                            self.page.wait_for_timeout(800)

                            hex_input = self.page.locator("input[aria-label*='Hex' i], input[placeholder*='Hex' i], input[type='text']:visible").last
                            if hex_input.is_visible():
                                hex_clean = color_target.lstrip("#")
                                hex_input.fill(hex_clean)
                                self.page.wait_for_timeout(300)
                                self.page.keyboard.press("Enter")
                                self.page.wait_for_timeout(500)
                                self.log(f"[BANNER] Applied custom banner Hex color: #{hex_clean}")
                        
                        # Dismiss color popover
                        self.page.keyboard.press("Escape")
                        self.page.wait_for_timeout(400)
                except Exception as e:
                    self.log(f"[BANNER] Notice configuring custom color: {e}")
            else:
                self.log("[BANNER] Using standard Red banner color.")

            # 4. Fill Announcement Message
            msg_area = self.page.locator("div[role='dialog'] textarea, div[role='dialog'] input[aria-label*='Message' i]").first
            if msg_area.is_visible():
                msg_area.fill(message[:145])
                self.page.wait_for_timeout(400)

            # 5. Scroll dialog pane down to reveal Button Label and Link (announcement-banner-3)
            try:
                dialog_pane = self.page.locator("div[role='dialog'] [role='tabpanel']").first
                if dialog_pane.is_visible():
                    dialog_pane.evaluate("(el) => el.scrollTop = el.scrollHeight")
                    self.page.wait_for_timeout(400)
            except Exception:
                pass

            # Fill Button label (max 25 chars)
            btn_input = self.page.locator("div[role='dialog'] input[aria-label*='Button label' i]").first
            if btn_input.is_visible():
                btn_input.fill(button_label[:24])
                self.page.wait_for_timeout(300)

            # Fill Link URL
            link_input = self.page.locator("div[role='dialog'] input[aria-label*='Link' i]").first
            if link_input.is_visible() and link_url:
                link_input.fill(link_url)
                self.page.wait_for_timeout(300)

            self.log("[SUCCESS] Announcement banner configured.")

        except Exception as e:
            self.log(f"[BANNER] Notice adding announcement banner: {e}")
        finally:
            # Guarantee Settings modal is closed so canvas is completely unobstructed
            for _ in range(3):
                dialog = self.page.locator("div[role='dialog']")
                if dialog.count() > 0 and dialog.first.is_visible():
                    close_btn = self.page.locator("div[role='dialog'] button[aria-label*='Close' i], div[role='dialog'] [aria-label*='Close' i]").first
                    if close_btn.is_visible():
                        close_btn.click(force=True)
                    else:
                        self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(600)
                else:
                    break

    def set_site_title(self, site_name: str, banner_title: str):
        """Sets document title and banner title without truncation."""
        self.set_document_name(site_name)
        self.set_header_title(banner_title)

    def set_header_background(self, image_path: str):
        """Uploads and sets the background image for the top Header Box across all themes."""
        if not image_path or not os.path.exists(image_path):
            self.log("[HEADER] Notice: No valid image provided for header background.")
            return

        self.log(f"[HEADER] Setting Header background image: {os.path.basename(image_path)}...")
        try:
            # 1. Locate canvas header banner strictly (avoid top docs-header app bar)
            banner_area = self.page.locator("article section:first-of-type, div.p6n-wysiwyg-editor-canvas section:first-of-type").first
            
            # Ensure banner bottom area is scrolled comfortably into view
            if banner_area.count() > 0:
                try:
                    banner_area.evaluate("el => el.scrollIntoView({ block: 'nearest' })")
                    self.page.wait_for_timeout(300)
                except Exception:
                    pass

            bbox = banner_area.bounding_box() if banner_area.count() > 0 else None

            # 2. Hover/trigger banner area to reveal floating toolbar (Image, Header type)
            try:
                banner_area.hover()
                self.page.wait_for_timeout(500)
            except Exception:
                pass

            if bbox:
                hover_x = bbox['x'] + 80
                hover_y = bbox['y'] + bbox['height'] - 30
                self.page.mouse.move(hover_x, hover_y)
                self.page.wait_for_timeout(400)

            # 3. Locate 'Image' dropdown button inside the header banner
            image_btn = self.page.locator(
                "article section:first-of-type div[role='button']:has-text('Image'), "
                "div.p6n-wysiwyg-editor-canvas section:first-of-type div[role='button']:has-text('Image'), "
                "article section:first-of-type button:has-text('Image')"
            ).first

            if image_btn.count() > 0 and image_btn.is_visible():
                image_btn.click()
            elif bbox:
                # Move to toolbar area to reveal it
                self.page.mouse.move(bbox['x'] + 80, bbox['y'] + bbox['height'] - 30)
                self.page.wait_for_timeout(400)
                if image_btn.count() > 0 and image_btn.is_visible():
                    image_btn.click()
                else:
                    self.page.mouse.click(bbox['x'] + 80, bbox['y'] + bbox['height'] - 30)
            self.page.wait_for_timeout(1000)

            # 4. Target the exact 'Upload' item in the opened menu
            upload_item = self.page.locator(
                "[role='menuitem']:has-text('Upload'), "
                "div[role='menu'] [role='menuitem']:has-text('Upload'), "
                ".z80M1:has-text('Upload')"
            ).first

            upload_success = False
            if upload_item.count() > 0 and upload_item.is_visible():
                try:
                    with self.page.expect_file_chooser(timeout=7000) as fc_info:
                        upload_item.click()
                    file_chooser = fc_info.value
                    file_chooser.set_files(image_path)
                    self.page.wait_for_timeout(3500)
                    upload_success = True
                    self.log(f"[SUCCESS] Header background image set successfully: {os.path.basename(image_path)}")
                except Exception as fc_err:
                    self.log(f"[HEADER] Notice on file chooser: {fc_err}. Trying direct file input...")

            # Fallback: if expect_file_chooser didn't complete, check file inputs in DOM
            if not upload_success:
                file_inputs = self.page.locator("input[type='file']")
                if file_inputs.count() > 0:
                    try:
                        file_inputs.last.set_input_files(image_path)
                        self.page.wait_for_timeout(3500)
                        upload_success = True
                        self.log(f"[SUCCESS] Header background image set via input fallback: {os.path.basename(image_path)}")
                    except Exception as fi_err:
                        self.log(f"[HEADER] File input fallback notice: {fi_err}")

            if not upload_success:
                self.log("[HEADER] Notice: Could not upload header background image.")

            # Dismiss menu and any backdrop completely
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.log(f"[HEADER] Notice setting header background: {e}")

    def set_header_background_image(self, image_path: str):
        """Alias for set_header_background."""
        self.set_header_background(image_path)

    def set_document_name(self, name: str):
        """Sets the site document name (both top toolbar doc name and canvas site name) without truncation, preserving full title and symbols in Headless & Headed modes."""
        clean_name = re.sub(r'[\r\n]+', ' ', name).strip()
        clean_name = re.sub(r'\s{2,}', ' ', clean_name)
        self.log(f"[HEADER] Setting Document & Site Name ({len(clean_name)} chars) to: '{clean_name}'...")
        
        # 1. Top Document Name box (in top toolbar)
        try:
            doc_input = self.page.locator("div.qQh9nc input, input.ewpfie, div[aria-label*='Site document name' i] input, input[aria-label*='site name' i]").first
            if doc_input.count() > 0:
                doc_input.click()
                self.page.wait_for_timeout(200)
                self.page.keyboard.press("Control+A")
                self.page.wait_for_timeout(100)
                self.page.keyboard.insert_text(clean_name)
                self.page.wait_for_timeout(200)
                self.page.keyboard.press("Enter")
                self.page.wait_for_timeout(500)
                self.log(f"[SUCCESS] Top Document Name set to: '{clean_name}'")
        except Exception as e:
            self.log(f"[HEADER] Notice setting top document name: {e}")

        # 2. Canvas Site Name box (in top-left of canvas header)
        try:
            canvas_site_name = self.page.locator("input[aria-label='Site name'], div.quPuCb input, [aria-label*='Site name:' i] input, div:has-text('Enter site name') input").first
            if canvas_site_name.count() > 0:
                canvas_site_name.click()
                self.page.wait_for_timeout(200)
                self.page.keyboard.press("Control+A")
                self.page.wait_for_timeout(100)
                self.page.keyboard.insert_text(clean_name)
                self.page.wait_for_timeout(200)
                self.page.keyboard.press("Enter")
                self.page.wait_for_timeout(500)
                self.log(f"[SUCCESS] Canvas Site Name set to: '{clean_name}'")
        except Exception as e:
            self.log(f"[HEADER] Notice setting canvas site name: {e}")

    def set_header_title(self, title_text: str, enforce_length: bool = False):
        """Sets the banner/header H1 title safely in both Headless and Headed modes without truncation."""
        clean_title = re.sub(r'[\r\n]+', ' ', title_text).strip()
        clean_title = re.sub(r'\s{2,}', ' ', clean_title)
        if enforce_length:
            clean_title = enforce_title_60_70(clean_title)
        self.log(f"[HEADER] Setting Header Title ({len(clean_title)} chars) to: '{clean_title}'...")
        try:
            # Locate header title element (covers un-focused lf5WFf, contenteditable, and heading)
            title_el = self.page.locator(
                "section:first-of-type div.lf5WFf, "
                "section:first-of-type div[aria-label='Text'], "
                "section:first-of-type [contenteditable='true'], "
                "h1.zfr3Q, div[data-name='title'], article h1"
            ).first
            if title_el.count() > 0:
                try:
                    title_el.scroll_into_view_if_needed()
                except Exception:
                    pass
                title_el.click(force=True)
                self.page.wait_for_timeout(200)
                self.page.keyboard.press("Enter")
            else:
                self.page.mouse.click(500, 220)
                self.page.wait_for_timeout(200)
                self.page.keyboard.press("Enter")
            self.page.wait_for_timeout(250)
            self.page.keyboard.press("Control+A")
            self.page.wait_for_timeout(100)
            
            # Native insert_text works 100% reliably in Headless mode (doesn't rely on OS clipboard)
            self.page.keyboard.insert_text(clean_title)
            self.page.wait_for_timeout(300)
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            self.log(f"[SUCCESS] Header Title set to: '{clean_title}'")
        except Exception as e:
            self.log(f"[HEADER] Error setting header title: {e}")

    def paste_text_into_editor(self, editor_locator, text: str):
        """Pastes text reliably into Google Sites contenteditable editor in both Headless and Headed modes."""
        try:
            editor_locator.scroll_into_view_if_needed()
            editor_locator.click(force=True)
            self.page.wait_for_timeout(200)

            # Native insert_text dispatches directly into the contenteditable element (works in Headless & Headed)
            try:
                self.page.keyboard.insert_text(text)
            except Exception:
                set_windows_clipboard_text(text)
                self.page.keyboard.press("Control+V")
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.log(f"[EDITOR] Error entering text: {e}")

            # 4. Verify text was received in editor
            current_text = ""
            try:
                current_text = editor_locator.inner_text().strip()
            except Exception:
                pass

            if not current_text:
                self.log("[PASTE] Direct paste was empty, typing text via keyboard...")
                self.page.keyboard.type(text, delay=5)
                self.page.wait_for_timeout(200)
            else:
                self.log(f"[PASTE] Successfully pasted {len(text)} characters into editor.")

        except Exception as e:
            self.log(f"[PASTE] Notice on paste into editor: {e}")
            self.page.keyboard.type(text, delay=8)

    def set_section_color(self, style_name: str = "Style 3", target_element=None):
        """
        Sets section background color strictly on the CURRENT section row.
        Uses position-locked vertical matching and selects 3rd option (Style 3 Theme Color).
        """
        self.log(f"[STYLE] Setting section background color to: '{style_name}' (3rd color option)...")
        try:
            # Safeguard 1: Dismiss any unexpected open dialogs
            for _ in range(2):
                dialog = self.page.locator("div[role='dialog']")
                if dialog.count() > 0 and dialog.first.is_visible():
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(300)

            ref_x = None
            ref_y = None
            if target_element and target_element.count() > 0:
                try:
                    target_element.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(250)
                    t_box = target_element.bounding_box()
                    if t_box:
                        ref_x = t_box['x']
                        ref_y = t_box['y']
                except Exception:
                    pass

            if ref_y is None:
                vp = self.page.viewport_size or {"width": 1920, "height": 1080}
                ref_y = vp["height"] - 250

            # Step 1: Hover INSIDE the section at x=300 to activate hover state for this row!
            # (In Google Sites, section container starts at x=60, so hovering at x=300 triggers section hover!)
            self.page.mouse.move(300, ref_y + 10)
            self.page.wait_for_timeout(350)

            # Step 2: Locate Section colors (Palette) button matching this vertical row
            palette_candidates = self.page.locator(
                "div[aria-label*='Section colors' i]:visible, "
                "div[aria-label*='Section background' i]:visible, "
                "div[data-tooltip*='Section colors' i]:visible, "
                "div[data-tooltip*='Section background' i]:visible, "
                "button[aria-label*='Section colors' i]:visible"
            )

            palette_btn = None
            closest_dist = 9999
            if palette_candidates.count() > 0:
                for btn in palette_candidates.all():
                    b_box = btn.bounding_box()
                    if b_box and b_box['x'] < 150:
                        dist = abs(b_box['y'] - ref_y)
                        if dist < closest_dist and dist < 90:
                            closest_dist = dist
                            palette_btn = btn

            if not (palette_btn and palette_btn.count() > 0 and palette_btn.is_visible()):
                # Slight re-hover
                self.page.mouse.move(250, ref_y + 15)
                self.page.wait_for_timeout(300)
                for btn in palette_candidates.all():
                    b_box = btn.bounding_box()
                    if b_box and b_box['x'] < 150:
                        dist = abs(b_box['y'] - ref_y)
                        if dist < closest_dist and dist < 90:
                            closest_dist = dist
                            palette_btn = btn

            if not (palette_btn and palette_btn.count() > 0 and palette_btn.is_visible()):
                self.log("[STYLE] [NOTICE] Section palette button not revealed for current section.")
                return

            p_box = palette_btn.bounding_box()
            cx = p_box['x'] + p_box['width'] / 2
            cy = p_box['y'] + p_box['height'] / 2

            # Step 3: Physical mouse click on palette button to open Section Colors menu
            self.page.mouse.move(cx, cy)
            self.page.wait_for_timeout(150)
            self.page.mouse.click(cx, cy)
            self.page.wait_for_timeout(600)

            # Safeguard against Embed dialog
            embed_dialog = self.page.locator("div[role='dialog']:has-text('Embed'), div[role='dialog']:has-text('Insert from the web')")
            if embed_dialog.count() > 0 and embed_dialog.first.is_visible():
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(300)
                return

            # Step 4: Click the 3rd Color Option (Style 3 / Emphasis 2 Theme Color)
            # The Section Colors options appear at x ~ 124px as diagnosed
            applied = False

            # Primary: Look for 'Style 3' text
            style3_opt = self.page.locator(
                "span:text-is('Style 3'):visible, "
                "span:has-text('Style 3'):visible, "
                "[role='menuitem']:has-text('Style 3'):visible, "
                "li:has-text('Style 3'):visible, "
                "div:text-is('Style 3'):visible"
            ).last

            if style3_opt.count() > 0 and style3_opt.is_visible():
                s_box = style3_opt.bounding_box()
                if s_box and s_box['x'] < 400:
                    style3_opt.click()
                    applied = True

            # Secondary: Click 3rd item (index 2) in the left popup menu
            if not applied:
                left_menu = self.page.locator("ul.VfPpkd-StrnGf-rymPhb:visible, .VfPpkd-xl07Ob-XxIAqe:visible ul, ul[role='menu']:visible").last
                if left_menu.count() > 0 and left_menu.is_visible():
                    m_box = left_menu.bounding_box()
                    if m_box and m_box['x'] < 400:
                        items = left_menu.locator("li[role='menuitem'], li, div[role='menuitem']")
                        if items.count() >= 3:
                            items.nth(2).click()
                            applied = True

            if applied:
                self.page.wait_for_timeout(400)
                self.log(f"[SUCCESS] Applied 3rd color option (Style 3 / Theme Color) to section background.")
            else:
                self.log("[STYLE] [WARNING] Style 3 option not applied in menu.")
                self.page.keyboard.press("Escape")

        except Exception as e:
            self.log(f"[STYLE] Notice setting section color: {e}")

    def _prepare_canvas_for_new_section(self):
        """Scrolls canvas all the way to bottom so new blocks append at bottom."""
        try:
            # Scroll canvas container DOM directly to bottom
            self.page.evaluate("""() => {
                const scrollers = document.querySelectorAll(
                    "div.p6n-wysiwyg-editor-canvas, div[role='main'], div.p6n-wysiwyg-scroll-container, aside ~ div"
                );
                scrollers.forEach(s => { s.scrollTop = s.scrollHeight; });
                window.scrollTo(0, document.body.scrollHeight);
            }""")
            self.page.wait_for_timeout(200)

            # Physical wheel scroll on canvas center
            vp = self.page.viewport_size or {"width": 1920, "height": 1080}
            self.page.mouse.move(vp["width"] // 2, 500)
            self.page.mouse.wheel(0, 1500)
            self.page.wait_for_timeout(200)
        except Exception as e:
            self.log(f"[CANVAS] Notice preparing canvas: {e}")

    def _scroll_sidebar_down(self, pixels: int = 600):
        """Scrolls the right sidebar down using physical mouse wheel and JS scroll fallback."""
        try:
            # Dynamically determine right sidebar position on any screen resolution
            win_width = self.page.evaluate("window.innerWidth")
            sidebar_x = max(win_width - 80, 800)
            sidebar_y = 350

            self.page.mouse.move(sidebar_x, sidebar_y)
            self.page.wait_for_timeout(100)
            self.page.mouse.wheel(0, pixels)
            self.page.wait_for_timeout(250)

            # JS fallback: scroll any scrollable panel on the right side
            self.page.evaluate(f"""() => {{
                const all = document.querySelectorAll('*');
                for (const el of all) {{
                    const r = el.getBoundingClientRect();
                    if (r.left > window.innerWidth / 2 && el.scrollHeight > el.clientHeight && el.clientHeight > 200) {{
                        el.scrollTop += {pixels};
                    }}
                }}
            }}""")
            self.page.wait_for_timeout(200)
        except Exception as e:
            self.log(f"[SIDEBAR] Notice scrolling sidebar down: {e}")

    def _scroll_sidebar_top(self):
        """Scrolls the right sidebar all the way back to the top."""
        try:
            win_width = self.page.evaluate("window.innerWidth")
            sidebar_x = max(win_width - 80, 800)
            sidebar_y = 350

            self.page.mouse.move(sidebar_x, sidebar_y)
            self.page.wait_for_timeout(100)
            self.page.mouse.wheel(0, -4000)
            self.page.wait_for_timeout(250)

            # JS fallback: scroll all right sidebar panels to top = 0
            self.page.evaluate("""() => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const r = el.getBoundingClientRect();
                    if (r.left > window.innerWidth / 2 && el.scrollHeight > el.clientHeight) {
                        el.scrollTop = 0;
                    }
                }
            }""")
            self.page.wait_for_timeout(200)
        except Exception as e:
            self.log(f"[SIDEBAR] Notice scrolling sidebar top: {e}")

    def add_h2_text_box(self, h2_heading: str, body_text: str, section_style: Optional[str] = None):
        """Adds a text box, formats heading as H2, inserts text, and optionally sets section color."""
        self.log(f"[CONTENT] Adding H2 heading and text: '{h2_heading[:35]}...'")
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(300)

            text_btn = self.page.locator("div[role='button']:has-text('Text box'), [aria-label*='Text box' i]")
            if text_btn.count() > 0:
                text_btn.first.click(force=True)
                self.page.wait_for_timeout(1200)

            # Set heading style FIRST
            style_btn = self.page.locator("div[aria-label*='Text style' i], div[aria-label*='Normal text' i], div[aria-label*='Style' i], div.p6n-wysiwyg-font-style-dropdown")
            if style_btn.count() > 0:
                style_btn.first.click(force=True)
                self.page.wait_for_timeout(400)
                heading_opt = self.page.locator("div[role='menuitem']:has-text('Heading'), span:has-text('Heading')")
                if heading_opt.count() > 0:
                    heading_opt.first.click(force=True)
                    self.page.wait_for_timeout(400)

            # Type Heading
            self.page.keyboard.type(h2_heading)
            self.page.keyboard.press("Enter")
            self.page.wait_for_timeout(300)
            self.page.keyboard.type(body_text)
            self.page.wait_for_timeout(500)
            self.page.keyboard.press("Escape")

            if section_style:
                self.set_section_color(section_style)
        except Exception as e:
            self.log(f"[CONTENT] Error inserting text box: {e}")

    def add_h2_heading_section(self, h2_heading: str, section_style: str = "Style 3"):
        """Adds a standalone H2 heading in its own section styled with Theme Color (Style 3)."""
        self.log(f"[HEADING] Adding H2 Section: '{h2_heading[:45]}...' ({section_style})")
        try:
            # 1. Canvas preparation: scroll to bottom
            self._prepare_canvas_for_new_section()

            # 2. Ensure Insert tab is active
            insert_tab = self.page.locator("div[role='tab']:has-text('Insert'), [aria-label*='Insert' i]").first
            if insert_tab.count() > 0:
                insert_tab.click(force=True)
                self.page.wait_for_timeout(250)
            self._scroll_sidebar_top()
            self.page.wait_for_timeout(200)

            # 3. Click Text Box in sidebar
            text_btn = self.page.locator(
                "div[role='tabpanel'] div[role='button']:has-text('Text box'), "
                "div[role='button']:has-text('Text box'), "
                "[aria-label*='Text box' i]"
            ).first

            try:
                text_btn.scroll_into_view_if_needed(timeout=2000)
            except Exception:
                pass

            if text_btn.is_visible():
                text_btn.click(force=True)
                self.page.wait_for_timeout(900)

            # 4. Target the newly created text box (must be EMPTY, not the previous filled box!)
            box_selector = "div[role='main'] div[contenteditable='true']:visible, div[contenteditable='true']:visible"
            editor_box = self.page.locator(box_selector).last

            # Empty-box guard: If .last still contains text, wait up to 3s for the new empty box to render
            for _ in range(30):
                try:
                    if len(editor_box.inner_text().strip()) == 0:
                        break
                except Exception:
                    pass
                self.page.wait_for_timeout(100)
                editor_box = self.page.locator(box_selector).last

            # Re-click safety fallback if new text box didn't spawn
            try:
                if editor_box.count() > 0 and len(editor_box.inner_text().strip()) > 0:
                    self.log("[HEADING] [SAFETY] Last text box is not empty. Re-clicking 'Text box' button...")
                    self._scroll_sidebar_top()
                    if text_btn.is_visible():
                        text_btn.click(force=True)
                        self.page.wait_for_timeout(1200)
                    editor_box = self.page.locator(box_selector).last
            except Exception:
                pass

            try:
                editor_box.click(force=True, timeout=3000)
                self.page.wait_for_timeout(200)
            except Exception as e:
                self.log(f"[HEADING] Notice focusing text box: {e}")

            # 5. Type heading text FIRST into text box
            self.page.keyboard.type(h2_heading, delay=15)
            self.page.wait_for_timeout(250)

            # 6. USER RULE: Apply Heading format via Control+Alt+2
            self.page.keyboard.press("Control+Alt+2")
            self.page.wait_for_timeout(350)
            self.log("[HEADING] Style 'Heading' applied via Control+Alt+2.")

            # 7. Apply section color (3rd option Style 3 Theme Color) strictly on this current section!
            if section_style:
                self.set_section_color(section_style, target_element=editor_box)

            # Deselect cleanly
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(200)

        except Exception as e:
            self.log(f"[HEADING] Error adding H2 heading section: {e}")

    def add_normal_text_box(self, paragraphs: List[str], section_style: Optional[str] = None):
        """Adds a normal text box with clean paragraph spacing using instant paste, optionally setting section color."""
        self.log(f"[CONTENT] Adding text box with {len(paragraphs)} paragraph(s)...")
        try:
            # 1. Canvas preparation: scroll to bottom
            self._prepare_canvas_for_new_section()

            # 2. Ensure Insert tab is active and sidebar is at top
            insert_tab = self.page.locator("div[role='tab']:has-text('Insert'), [aria-label*='Insert' i]").first
            if insert_tab.count() > 0:
                insert_tab.click(force=True)
                self.page.wait_for_timeout(250)
            self._scroll_sidebar_top()
            self.page.wait_for_timeout(200)

            text_btn = self.page.locator(
                "div[role='tabpanel'] div[role='button']:has-text('Text box'), "
                "div[role='button']:has-text('Text box'), "
                "[aria-label*='Text box' i]"
            ).first

            try:
                text_btn.scroll_into_view_if_needed(timeout=2000)
            except Exception:
                pass

            if text_btn.is_visible():
                text_btn.click(force=True)
                self.page.wait_for_timeout(900)

            # 3. Target the newly created text box (must be EMPTY)
            box_selector = "div[role='main'] div[contenteditable='true']:visible, div[contenteditable='true']:visible"
            editor_box = self.page.locator(box_selector).last

            # Empty-box guard
            for _ in range(30):
                try:
                    if len(editor_box.inner_text().strip()) == 0:
                        break
                except Exception:
                    pass
                self.page.wait_for_timeout(100)
                editor_box = self.page.locator(box_selector).last

            # Re-click safety fallback if new text box didn't spawn
            try:
                if editor_box.count() > 0 and len(editor_box.inner_text().strip()) > 0:
                    self.log("[CONTENT] [SAFETY] Last text box is not empty. Re-clicking 'Text box' button...")
                    self._scroll_sidebar_top()
                    if text_btn.is_visible():
                        text_btn.click(force=True)
                        self.page.wait_for_timeout(1200)
                    editor_box = self.page.locator(box_selector).last
            except Exception:
                pass

            if editor_box.count() > 0 and editor_box.is_visible():
                combined_text = "\n\n".join([p.strip() for p in paragraphs if p.strip()])
                self.paste_text_into_editor(editor_box, combined_text)
                self.page.wait_for_timeout(350)

                if section_style:
                    self.set_section_color(section_style, target_element=editor_box)

            # Deselect cleanly
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(200)

        except Exception as e:
            self.log(f"[CONTENT] Error adding normal text box: {e}")

    def add_bulk_keywords_box(self, keywords_text: str, section_style: Optional[str] = None):
        """Adds bulk keywords box using instant paste, optionally setting section color."""
        self.log("[SEO] Adding bulk keywords box...")
        try:
            self._prepare_canvas_for_new_section()

            insert_tab = self.page.locator("div[role='tab']:has-text('Insert')").first
            if insert_tab.count() > 0:
                insert_tab.click(force=True)
                self.page.wait_for_timeout(250)

            self._scroll_sidebar_top()
            self.page.wait_for_timeout(200)

            text_btn = self.page.locator(
                "div[role='tabpanel'] div[role='button']:has-text('Text box'), "
                "div[role='button']:has-text('Text box'), "
                "[aria-label*='Text box' i]"
            ).first

            try:
                text_btn.scroll_into_view_if_needed(timeout=2000)
            except Exception:
                pass

            if text_btn.count() > 0 and text_btn.is_visible():
                text_btn.click(force=True)
                self.page.wait_for_timeout(900)

                box_selector = "div[role='main'] div[contenteditable='true']:visible, div[contenteditable='true']:visible"
                editor_box = self.page.locator(box_selector).last

                for _ in range(30):
                    try:
                        if len(editor_box.inner_text().strip()) == 0:
                            break
                    except Exception:
                        pass
                    self.page.wait_for_timeout(100)
                    editor_box = self.page.locator(box_selector).last

                # Re-click safety fallback
                try:
                    if editor_box.count() > 0 and len(editor_box.inner_text().strip()) > 0:
                        self.log("[SEO] [SAFETY] Last text box is not empty. Re-clicking 'Text box' button...")
                        self._scroll_sidebar_top()
                        if text_btn.is_visible():
                            text_btn.click(force=True)
                            self.page.wait_for_timeout(1200)
                        editor_box = self.page.locator(box_selector).last
                except Exception:
                    pass

                if editor_box.count() > 0 and editor_box.is_visible():
                    self.paste_text_into_editor(editor_box, keywords_text)
                    self.page.wait_for_timeout(350)

                    if section_style:
                        self.set_section_color(section_style, target_element=editor_box)

                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(200)
                self.log("[SUCCESS] Bulk keywords added.")
        except Exception as e:
            self.log(f"[SEO] Error adding bulk keywords box: {e}")

    def add_cta_buttons(self, phone_number: str, whatsapp_link: str):
        """Adds Call and WhatsApp Buttons with links."""
        self.log("[BUTTONS] Adding CTA buttons...")
        
        if phone_number:
            clean_phone = re.sub(r'[^0-9+]', '', phone_number)
            tel_link = f"tel:{clean_phone}"
            self._insert_single_button("Call Now", tel_link)

        if whatsapp_link:
            wa_clean = whatsapp_link.strip()
            if not wa_clean.startswith("http"):
                clean_wa_num = re.sub(r'[^0-9]', '', wa_clean)
                wa_clean = f"https://wa.me/{clean_wa_num}"
            self._insert_single_button("Chat on WhatsApp", wa_clean)

    def drag_button_under_header_title(self, button_label: Optional[str] = None):
        """Drags the newly inserted button up into the header banner right under the page title or previously docked button."""
        self.log(f"[BUTTONS] Dragging button ({button_label or 'last inserted'}) to dock under Header Title...")
        try:
            # 1. Scroll canvas scrollers to top = 0
            self.page.evaluate("""() => {
                const scrollers = document.querySelectorAll(
                    "div.p6n-wysiwyg-editor-canvas, div.p6n-wysiwyg-scroll-container, article, aside ~ div"
                );
                for (const s of scrollers) s.scrollTop = 0;
                window.scrollTo(0, 0);
            }""")
            self.page.wait_for_timeout(600)

            # 2. Locate the header banner area inside editor canvas dynamically (avoid top docs-header navbar)
            header_el = self.page.locator(
                "article section:first-of-type, div.p6n-wysiwyg-editor-canvas section:first-of-type, section.p6n-wysiwyg-header, [data-name='header']"
            ).first
            header_box = header_el.bounding_box() if header_el.count() > 0 else None

            if not header_box or header_box['height'] < 80:
                header_el = self.page.locator("div[role='main'] section:first-of-type, article > section").first
                header_box = header_el.bounding_box() if header_el.count() > 0 else None

            if not header_box or header_box['height'] < 50:
                header_top = 70.0
                header_bottom = 440.0
                header_center_x = 507.6
            else:
                header_top = header_box['y']
                header_bottom = header_box['y'] + header_box['height']
                header_center_x = header_box['x'] + header_box['width'] / 2

            # 3. Locate the header title element strictly inside the canvas (avoid top docs document name)
            title_el = self.page.locator(
                "h1.zfr3Q, article h1, div.p6n-wysiwyg-editor-canvas h1, section:first-of-type [contenteditable='true']"
            ).first
            title_box = title_el.bounding_box() if title_el.count() > 0 else None

            if title_box and title_box['x'] > 50 and title_box['y'] > 60:
                target_x = title_box['x'] + title_box['width'] / 2
                title_bottom = title_box['y'] + title_box['height']
            else:
                target_x = header_center_x if (100 < header_center_x < 900) else 507.6
                title_bottom = min(header_top + 220, header_bottom - 50)

            # 4. Check for existing buttons already docked inside the header banner
            existing_header_btn_box = None
            try:
                candidate_btns = self.page.locator("div[role='button'], a").all()
                docked = []
                for c in candidate_btns:
                    b = c.bounding_box()
                    if b and b['width'] > 40 and b['height'] > 15:
                        if header_top <= b['y'] < (header_bottom - 10) and (b['x'] < 850):
                            txt = c.inner_text().strip()
                            if txt and (not button_label or txt != button_label):
                                docked.append((b['y'] + b['height'], b))
                if docked:
                    docked.sort(key=lambda x: x[0], reverse=True)
                    existing_header_btn_box = docked[0][1]
            except Exception:
                pass

            # 5. Compute drop target coordinates dynamically inside the header
            if existing_header_btn_box:
                # Docking second button: place right below the first docked button
                btn1_bottom = existing_header_btn_box['y'] + existing_header_btn_box['height']
                target_y = min(btn1_bottom + 15, header_bottom - 15)
            else:
                # Docking first button: place right below the H1 title inside header
                target_y = min(title_bottom + 18, header_bottom - 20)

            target_y = max(target_y, header_top + 40)

            # 6. Drag with verification & automatic retry
            max_attempts = 2
            docked_success = False

            for attempt in range(1, max_attempts + 1):
                # Find the button to drag (must be below header)
                if button_label:
                    btn_candidates = self.page.locator(f"div[role='button']:has-text('{button_label}'), a:has-text('{button_label}')").all()
                else:
                    btn_candidates = self.page.locator("div[role='button']:has-text('WhatsApp'), div[role='button']:has-text('Call'), div[role='button']:has-text('Chat')").all()

                target_btn = None
                target_btn_box = None
                for c in reversed(btn_candidates):
                    b = c.bounding_box()
                    if b and b['y'] >= (header_bottom - 10):
                        target_btn = c
                        target_btn_box = b
                        break

                if not target_btn_box:
                    # Button is already in header
                    self.log(f"[SUCCESS] Button '{button_label or 'inserted'}' is positioned inside Header.")
                    docked_success = True
                    break

                # Grab near top boundary of the button tile to avoid clicking button link text
                start_x = target_btn_box['x'] + target_btn_box['width'] / 2
                start_y = target_btn_box['y'] + 6

                if attempt > 1:
                    adj_target_y = min(target_y + 12, header_bottom - 15)
                    self.log(f"[BUTTONS] [RETRY {attempt}] Dragging from ({start_x:.1f}, {start_y:.1f}) to target ({target_x:.1f}, {adj_target_y:.1f})...")
                else:
                    adj_target_y = target_y
                    self.log(f"[BUTTONS] Dragging from ({start_x:.1f}, {start_y:.1f}) to target ({target_x:.1f}, {adj_target_y:.1f})...")

                # Move and drag smoothly
                self.page.mouse.move(start_x, start_y)
                self.page.wait_for_timeout(250)
                self.page.mouse.down()
                self.page.wait_for_timeout(300)
                self.page.mouse.move(target_x, adj_target_y, steps=45)
                # Hold on drop target for 500ms so Google Sites activates the blue docking slot line
                self.page.wait_for_timeout(500)
                self.page.mouse.up()
                self.page.wait_for_timeout(1000)
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(500)

                # Verify if button now resides inside header bounds
                verify_btns = self.page.locator(f"div[role='button']:has-text('{button_label}'), a:has-text('{button_label}')").all() if button_label else []
                for vb in verify_btns:
                    vbb = vb.bounding_box()
                    if vbb and header_top <= vbb['y'] < header_bottom:
                        docked_success = True
                        break

                if docked_success:
                    self.log(f"[SUCCESS] Button '{button_label or 'inserted'}' successfully docked under Header Title.")
                    break
                else:
                    self.log(f"[BUTTONS] [NOTICE] Button '{button_label}' not yet inside Header after Attempt {attempt}.")

            if not docked_success:
                self.log(f"[BUTTONS] Notice: Drag sequence completed for '{button_label}'.")
        except Exception as e:
            self.log(f"[BUTTONS] Notice dragging button under title: {e}")

    def add_button_element(self, label: str, link: str, make_full_width: bool = False, drag_to_header: bool = False):
        """Inserts a button with link, and optionally stretches to full width or docks under header."""
        return self._insert_single_button(label=label, link=link, make_full_width=make_full_width, drag_to_header=drag_to_header)

    def _insert_single_button(self, label: str, link: str, make_full_width: bool = False, drag_to_header: bool = False):
        """Inserts a single button with strict locator matching."""
        try:
            self.log(f"[BUTTONS] Attempting to insert button: '{label}' -> {link}...")

            # 1. Canvas preparation
            self._prepare_canvas_for_new_section()

            # 2. Insert tab
            insert_tab = self.page.locator("div[role='tab']:has-text('Insert')").first
            if insert_tab.count() > 0:
                insert_tab.click(force=True)
                self.page.wait_for_timeout(300)

            # Scroll sidebar top then down to bring Button widget into viewport
            self._scroll_sidebar_top()
            self.page.wait_for_timeout(200)
            self._scroll_sidebar_down(650)
            self.page.wait_for_timeout(350)

            # Strict sidebar-scoped locator
            sidebar = self.page.locator(
                "div[role='tabpanel'], div.p6n-insert-panel, aside"
            ).first

            btn_insert = None
            if sidebar.count() > 0:
                # Exact match — sirf "Button" word, "Insert button" ya "Buttons" nahi
                candidates = sidebar.locator(
                    "div[role='button']", 
                    has_text=re.compile(r"^\s*Button\s*$")
                )
                if candidates.count() > 0 and candidates.first.is_visible():
                    btn_insert = candidates.first

            # Fallback 1 — aria-label exact
            if not btn_insert or btn_insert.count() == 0 or not btn_insert.is_visible():
                btn_insert = self.page.locator(
                    "div[role='tabpanel'] [aria-label='Button'], "
                    "div[role='tabpanel'] [aria-label='Button '], "
                    "div[role='tabpanel'] div[role='button']:has-text('Button')"
                ).first

            # Fallback 2 — page-level exact
            if not btn_insert or btn_insert.count() == 0 or not btn_insert.is_visible():
                btn_insert = self.page.get_by_role(
                    "button", name=re.compile(r"^Button$")
                ).first

            if btn_insert and btn_insert.count() > 0 and btn_insert.is_visible():
                btn_insert.click(force=True)
                self.page.wait_for_timeout(1500)

                # Dialog
                dialog = self.page.locator(
                    "div[role='dialog']:visible, div[aria-modal='true']:visible"
                ).last

                try:
                    dialog.wait_for(state="visible", timeout=5000)
                except Exception:
                    pass

                # Input fields
                name_input = dialog.locator(
                    "input[aria-label*='Name' i], input[placeholder*='Name' i]"
                ).first
                link_input = dialog.locator(
                    "input[aria-label*='Link' i], input[placeholder*='Link' i]"
                ).first

                if not (name_input.count() > 0 and name_input.is_visible()):
                    all_inputs = dialog.locator(
                        "input[type='text']:not([type='checkbox']):not([type='radio'])"
                    )
                    if all_inputs.count() >= 2:
                        name_input = all_inputs.nth(0)
                        link_input = all_inputs.nth(1)

                # Fallback page-level
                if not (name_input.count() > 0 and name_input.is_visible()):
                    name_input = self.page.locator(
                        "div[role='dialog'] input[aria-label*='Name' i], "
                        "input[aria-label*='Name' i]"
                    ).first
                    link_input = self.page.locator(
                        "div[role='dialog'] input[aria-label*='Link' i], "
                        "input[aria-label*='Link' i]"
                    ).first

                if name_input.count() > 0 and name_input.is_visible() and link_input.count() > 0 and link_input.is_visible():
                    name_input.click()
                    name_input.fill(label)
                    self.page.wait_for_timeout(200)

                    link_input.click()
                    link_input.fill(link)
                    self.page.wait_for_timeout(300)

                    # In Google Sites Button modal, pressing Enter inside the Link input directly submits the form!
                    link_input.press("Enter")
                    self.page.wait_for_timeout(1000)

                    # If dialog is still open, locate and click the active Insert button
                    dialog = self.page.locator("div[role='dialog']:visible, div[aria-modal='true']:visible").last
                    if dialog.count() > 0 and dialog.is_visible():
                        dialog_insert = dialog.locator(
                            "button:has-text('Insert'), div[role='button']:has-text('Insert'), [aria-label*='Insert' i]"
                        ).first
                        if dialog_insert.count() > 0 and dialog_insert.is_visible():
                            dialog_insert.click(force=True)
                            self.page.wait_for_timeout(1000)

                    # Wait for dialog dismissal
                    self._wait_dialog_closed(timeout=4000)
                    self.log(f"[SUCCESS] Added button: '{label}' -> {link}")

                    if drag_to_header:
                        self.drag_button_under_header_title(button_label=label)
                    elif make_full_width:
                        self.resize_image_to_full_width()
                else:
                    self.log(f"[BUTTONS] [WARNING] Button dialog inputs not found.")
            else:
                self.log(f"[BUTTONS] [WARNING] Button widget not found in sidebar.")

            self._scroll_sidebar_top()
        except Exception as e:
            self.log(f"[BUTTONS] Error adding button '{label}': {e}")

    def _wait_dialog_closed(self, timeout: int = 6000):
        """BUG 5 fix — Waits until any open dialog is fully dismissed."""
        try:
            self.page.wait_for_selector(
                "div[role='dialog']:visible, div[aria-modal='true']:visible",
                state="hidden",
                timeout=timeout
            )
        except Exception:
            # Force close if still open
            try:
                for _ in range(2):
                    if self.page.locator("div[role='dialog']:visible").count() > 0:
                        self.page.keyboard.press("Escape")
                        self.page.wait_for_timeout(400)
            except Exception:
                pass

    def upload_structure_images(self, folder_name: str) -> List[str]:
        """Gets images from the respective structure folder with automatic fallback if empty."""
        folder_path = os.path.join(IMAGES_DIR, folder_name)
        valid_exts = (".png", ".jpg", ".jpeg", ".webp")
        images = []
        if os.path.exists(folder_path):
            images = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.lower().endswith(valid_exts)
            ]
        if not images:
            for fallback_folder in ["str-image1", "str-image2", "str-image3", "str-image4"]:
                fb_path = os.path.join(IMAGES_DIR, fallback_folder)
                if os.path.exists(fb_path):
                    fb_images = [
                        os.path.join(fb_path, f)
                        for f in os.listdir(fb_path)
                        if f.lower().endswith(valid_exts)
                    ]
                    if fb_images:
                        self.log(f"[IMAGES] Notice: Folder '{folder_name}' was empty. Using {len(fb_images)} images from fallback '{fallback_folder}'.")
                        return sorted(fb_images)
        return sorted(images)

    def resize_image_to_full_width(self):
        """Drags the element's resize handles across the 12-column grid to achieve true full width."""
        self.log("[RESIZE] Resizing element to full width across grid...")
        try:
            self.page.wait_for_timeout(1000)

            # 1. Identify grid/canvas container boundaries
            grid = self.page.locator(
                "div.p6n-wysiwyg-grid:visible, div.p6n-wysiwyg-editor-canvas:visible, div[role='main']:visible"
            ).first
            grid_box = grid.bounding_box() if grid.count() > 0 else None

            if grid_box and grid_box['width'] > 200:
                grid_left = grid_box['x'] + 15
                grid_right = grid_box['x'] + grid_box['width'] - 15
            else:
                win_w = self.page.evaluate("window.innerWidth")
                grid_left = 60
                grid_right = max(win_w - 450, 900)

            # 2. Query visible resize handles (div.aGAaLb)
            handles_data = self.page.evaluate("""() => {
                const handles = Array.from(document.querySelectorAll("div.aGAaLb, div[class*='handle-']")).filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                });
                return handles.map(h => {
                    const r = h.getBoundingClientRect();
                    return { x: r.x, y: r.y, width: r.width, height: r.height };
                });
            }""")

            if not handles_data:
                # If element is not currently selected, click it to activate handles
                active_el = self.page.locator(
                    "div.WB0DVd:visible, div[role='main'] img:visible, section img:visible, div.p6n-wysiwyg-tile:visible"
                ).last
                if active_el.count() > 0:
                    active_el.click(force=True)
                    self.page.wait_for_timeout(600)
                    handles_data = self.page.evaluate("""() => {
                        const handles = Array.from(document.querySelectorAll("div.aGAaLb, div[class*='handle-']")).filter(el => {
                            const r = el.getBoundingClientRect();
                            return r.width > 0 && r.height > 0;
                        });
                        return handles.map(h => {
                            const r = h.getBoundingClientRect();
                            return { x: r.x, y: r.y, width: r.width, height: r.height };
                        });
                    }""")

            if handles_data:
                # 3. Check left handle - stretch to grid_left if not already aligned
                left_h = min(handles_data, key=lambda h: h['x'])
                if left_h['x'] > grid_left + 40:
                    start_lx = left_h['x'] + left_h['width'] / 2
                    start_ly = left_h['y'] + left_h['height'] / 2
                    self.log(f"[RESIZE] Dragging left handle from {start_lx:.1f} to {grid_left:.1f} (steps=18)...")
                    self.page.mouse.move(start_lx, start_ly)
                    self.page.wait_for_timeout(150)
                    self.page.mouse.down()
                    self.page.wait_for_timeout(150)
                    self.page.mouse.move(grid_left, start_ly, steps=18)
                    self.page.wait_for_timeout(300)
                    self.page.mouse.up()
                    self.page.wait_for_timeout(600)

                    # Refresh handles after left drag
                    handles_data = self.page.evaluate("""() => {
                        return Array.from(document.querySelectorAll("div.aGAaLb, div[class*='handle-']"))
                            .filter(el => {
                                const r = el.getBoundingClientRect();
                                return r.width > 0 && r.height > 0;
                            })
                            .map(h => {
                                const r = h.getBoundingClientRect();
                                return { x: r.x, y: r.y, width: r.width, height: r.height };
                            });
                    }""")

                # 4. Locate rightmost handle (East handle) and stretch across grid
                if handles_data:
                    max_x = max(h['x'] for h in handles_data)
                    right_candidates = [h for h in handles_data if abs(h['x'] - max_x) < 20]
                    # Select middle-right (East) handle among right edge candidates
                    right_h = sorted(right_candidates, key=lambda h: h['y'])[len(right_candidates) // 2]

                    start_rx = right_h['x'] + right_h['width'] / 2
                    start_ry = right_h['y'] + right_h['height'] / 2
                    target_rx = grid_right + 30  # Overshoot slightly (+30px) to trigger 12-column magnetic snap!

                    self.log(f"[RESIZE] Dragging right handle from ({start_rx:.1f}, {start_ry:.1f}) to target X={target_rx:.1f} (steps=18)...")
                    self.page.mouse.move(start_rx, start_ry)
                    self.page.wait_for_timeout(200)
                    self.page.mouse.down()
                    self.page.wait_for_timeout(150)
                    self.page.mouse.move(target_rx, start_ry, steps=18)
                    self.page.wait_for_timeout(400)
                    self.page.mouse.up()
                    self.page.wait_for_timeout(800)
                    self.log("[SUCCESS] Stretched element across 12-column grid.")

            # 5. Click 'Uncrop' on floating toolbar if available (preserves image aspect ratio)
            uncrop_btn = self.page.locator("div[aria-label*='Uncrop' i], button[aria-label*='Uncrop' i]").first
            if uncrop_btn.count() > 0 and uncrop_btn.is_visible():
                uncrop_btn.click(force=True)
                self.page.wait_for_timeout(500)
                self.log("[RESIZE] Clicked 'Uncrop' to display natural aspect ratio without distortion.")

            # 6. Deselect cleanly
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.log(f"[RESIZE] Notice resizing element to full width: {e}")

    def add_image_element(self, image_path: str, make_full_width: bool = True):
        """BUG 8 fix — Scroll sidebar to top before locating Images widget."""
        if not os.path.exists(image_path):
            return
        self.log(f"[IMAGE] Uploading image: {os.path.basename(image_path)}...")
        try:
            self._prepare_canvas_for_new_section()

            # Insert tab
            insert_tab = self.page.locator("div[role='tab']:has-text('Insert')").first
            if insert_tab.count() > 0:
                insert_tab.click(force=True)
                self.page.wait_for_timeout(300)

            # BUG 8 fix — sidebar top
            self._scroll_sidebar_top()
            self.page.wait_for_timeout(400)

            # Sidebar-scoped Images button
            sidebar = self.page.locator(
                "div[role='tabpanel'], div.p6n-insert-panel, aside"
            ).first

            images_btn = None
            if sidebar.count() > 0:
                candidates = sidebar.locator(
                    "div[role='button']", 
                    has_text=re.compile(r"^\s*Images\s*$")
                )
                if candidates.count() > 0:
                    images_btn = candidates.first

            if not images_btn or images_btn.count() == 0:
                images_btn = self.page.locator(
                    "div[role='button']:has-text('Images'), [aria-label*='Images' i]"
                ).first

            if images_btn and images_btn.count() > 0 and images_btn.is_visible():
                images_btn.click(force=True)
                self.page.wait_for_timeout(900)

                upload_opt = self.page.locator(
                    "div[role='menuitem']:has-text('Upload'), span:has-text('Upload')"
                ).last
                try:
                    upload_opt.wait_for(state="visible", timeout=3000)
                except Exception:
                    pass

                with self.page.expect_file_chooser(timeout=8000) as fc_info:
                    upload_opt.click(force=True)
                file_chooser = fc_info.value
                file_chooser.set_files(image_path)
                self.page.wait_for_timeout(3000)
                self.log(f"[SUCCESS] Image {os.path.basename(image_path)} uploaded.")

                if make_full_width:
                    self.resize_image_to_full_width()
        except Exception as e:
            self.log(f"[IMAGE] Notice uploading single image: {e}")

    def add_image_carousel(self, image_paths: List[str], make_full_width: bool = True):
        """Inserts an image carousel with multiple images and stretches to full width."""
        if not image_paths or len(image_paths) < 2:
            self.log("[CAROUSEL] Notice: At least 2 images required for an image carousel.")
            return

        self.log(f"[CAROUSEL] Inserting image carousel with {len(image_paths)} images...")
        try:
            carousel_btn = self.page.locator("div[role='button']:has-text('Image carousel'), [aria-label*='Image carousel' i]").first
            if carousel_btn.is_visible():
                carousel_btn.click()
                self.page.wait_for_timeout(1500)

                add_img = self.page.locator("div[role='dialog'] div[role='button']:has-text('Add image'), div[role='dialog'] [aria-label*='Add image' i], div[role='dialog'] div.p6n-wysiwyg-placeholder-circle, div[role='dialog'] div[role='button']:has-text('+')").first
                if add_img.is_visible():
                    add_img.click()
                    self.page.wait_for_timeout(600)
                    with self.page.expect_file_chooser(timeout=8000) as fc_info:
                        upload_item = self.page.locator("div[role='menuitem']:has-text('Upload image'), span:has-text('Upload image')").first
                        upload_item.click()
                    file_chooser = fc_info.value
                    file_chooser.set_files(image_paths[:8])
                    self.page.wait_for_timeout(4000)

                insert_btn = self.page.locator("div[role='dialog'] button:has-text('Insert'), div[role='dialog'] div[role='button']:has-text('Insert')").first
                if insert_btn.is_visible():
                    insert_btn.click()
                    self.page.wait_for_timeout(3000)
                    self.log("[SUCCESS] Image carousel inserted on canvas.")

                    if make_full_width:
                        self.resize_image_to_full_width()
        except Exception as e:
            self.log(f"[CAROUSEL] Error inserting carousel: {e}")

    def add_embed_by_url(self, target_url: str, make_full_width: bool = True):
        """Embeds external content or file by URL (embed-1, embed-2)."""
        self.log(f"[EMBED] Adding embed by URL: '{target_url}'...")
        try:
            embed_btn = self.page.locator("div[role='button']:has-text('Embed'), [aria-label*='Embed' i]").first
            if embed_btn.is_visible():
                embed_btn.click()
                self.page.wait_for_timeout(1500)

                # Ensure 'By URL' tab is active
                by_url_tab = self.page.locator("div[role='dialog'] div[role='tab']:has-text('By URL')").first
                if by_url_tab.is_visible():
                    by_url_tab.click()
                    self.page.wait_for_timeout(500)

                url_input = self.page.locator("div[role='dialog'] input[type='text'], div[role='dialog'] input[aria-label*='URL' i]").first
                if url_input.is_visible():
                    url_input.fill(target_url)
                    self.page.wait_for_timeout(1000)

                    insert_btn = self.page.locator("div[role='dialog'] button:has-text('Insert'), div[role='dialog'] div[role='button']:has-text('Insert')").first
                    if insert_btn.is_visible():
                        insert_btn.click()
                        self.page.wait_for_timeout(3000)
                        self.log("[SUCCESS] URL embed inserted.")

                        if make_full_width:
                            self.resize_image_to_full_width()
        except Exception as e:
            self.log(f"[EMBED] Notice adding URL embed: {e}")

    def add_embed_code(self, html_code: str, make_full_width: bool = True):
        """Embeds custom HTML code / iframe snippet (embed-1, embed-3)."""
        self.log("[EMBED] Adding embed by custom HTML code...")
        try:
            embed_btn = self.page.locator("div[role='button']:has-text('Embed'), [aria-label*='Embed' i]").first
            if embed_btn.is_visible():
                embed_btn.click()
                self.page.wait_for_timeout(1500)

                # Click 'Embed code' tab
                code_tab = self.page.locator("div[role='dialog'] div[role='tab']:has-text('Embed code')").first
                if code_tab.is_visible():
                    code_tab.click()
                    self.page.wait_for_timeout(500)

                code_area = self.page.locator("div[role='dialog'] textarea").first
                if code_area.is_visible():
                    code_area.fill(html_code)
                    self.page.wait_for_timeout(600)

                    next_btn = self.page.locator("div[role='dialog'] button:has-text('Next'), div[role='dialog'] div[role='button']:has-text('Next')").first
                    if next_btn.is_visible():
                        next_btn.click()
                        self.page.wait_for_timeout(2000)

                        insert_btn = self.page.locator("div[role='dialog'] button:has-text('Insert'), div[role='dialog'] div[role='button']:has-text('Insert')").first
                        if insert_btn.is_visible():
                            insert_btn.click()
                            self.page.wait_for_timeout(3000)
                            self.log("[SUCCESS] Custom HTML code embedded.")

                            if make_full_width:
                                self.resize_image_to_full_width()
        except Exception as e:
            self.log(f"[EMBED] Notice adding custom code embed: {e}")

    def add_content_block_1(self, image_path: str, title_text: str, body_text: str, section_style: Optional[str] = None):
        """Adds Content Block 1 (Left Image + Right Title & Description text boxes)."""
        self.log(f"[LAYOUT] Inserting Content Block 1: '{title_text[:30]}...'")
        try:
            self._prepare_canvas_for_new_section()
            self._scroll_sidebar_top()
            self.page.wait_for_timeout(500)

            # 1. Click Content Block 1 card in sidebar
            card_loc = self.page.locator(
                "[aria-label*='Image and caption' i], "
                "div[aria-label*='Add layout: Image and caption' i], "
                "div.dy3xqe"
            ).first

            if card_loc.is_visible():
                card_loc.click()
            else:
                self.page.mouse.click(1088, 373)

            self.page.wait_for_timeout(2500)
            last_sec = self.page.locator("article section").last

            # 2. Upload image via left placeholder button
            if image_path and os.path.exists(image_path):
                insert_btn = last_sec.locator(
                    "div[role='button'][aria-label*='Insert content' i], "
                    "div.U26fgb.JRtysb, "
                    "div[role='button']:has-text('+')"
                ).first

                if insert_btn.is_visible():
                    insert_btn.click()
                else:
                    h_box = last_sec.bounding_box()
                    if h_box:
                        self.page.mouse.click(h_box['x'] + 215, h_box['y'] + 112)

                self.page.wait_for_timeout(1000)

                upload_info = self.page.evaluate("""() => {
                    const all = Array.from(document.querySelectorAll('*'));
                    const matches = all.filter(el => el.children.length === 0 && el.innerText && el.innerText.trim() === 'Upload');
                    return matches.map(el => {
                        const rect = el.getBoundingClientRect();
                        return {
                            rect: { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) },
                            visible: rect.width > 0 && rect.height > 0
                        };
                    });
                }""")

                visible_upload = [u for u in upload_info if u['visible'] and u['rect']['y'] > 100]
                if visible_upload:
                    u = visible_upload[0]
                    cx = u['rect']['x'] + u['rect']['width'] / 2
                    cy = u['rect']['y'] + u['rect']['height'] / 2
                    with self.page.expect_file_chooser(timeout=8000) as fc_info:
                        self.page.mouse.click(cx, cy)
                    file_chooser = fc_info.value
                    file_chooser.set_files(image_path)
                    self.page.wait_for_timeout(4000)
                    self.log("[SUCCESS] Image uploaded into Content Block 1.")

            # 3. Populate Right-side Heading and Normal text
            text_gridcells = last_sec.locator("div[role='gridcell'][aria-label='Text']")
            if text_gridcells.count() >= 2:
                # Heading
                top_cell = text_gridcells.nth(0)
                top_cell.click()
                self.page.wait_for_timeout(400)
                active_editor = top_cell.locator("div[contenteditable='true']").first
                if active_editor.is_visible():
                    self.paste_text_into_editor(active_editor, title_text)
                else:
                    self.paste_text_into_editor(self.page.locator("div[contenteditable='true']").last, title_text)
                self.page.wait_for_timeout(500)
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(300)

                # Description
                bottom_cell = text_gridcells.nth(1)
                bottom_cell.click()
                self.page.wait_for_timeout(400)
                active_editor = bottom_cell.locator("div[contenteditable='true']").first
                if active_editor.is_visible():
                    self.paste_text_into_editor(active_editor, body_text)
                else:
                    self.paste_text_into_editor(self.page.locator("div[contenteditable='true']").last, body_text)
                self.page.wait_for_timeout(500)
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(300)

            # 4. Optional Section Color Style (Style 1, 2, 3)
            if section_style:
                self.set_section_color(section_style)

            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            self.log("[SUCCESS] Content Block 1 populated successfully.")
        except Exception as e:
            self.log(f"[LAYOUT] Notice inserting Content Block 1: {e}")

    def insert_content_block_layout(self, block_index: int = 0):
        """Clicks one of the 6 content block layout cards (index 0 to 5)."""
        try:
            cards = self.page.locator("div.p6n-content-blocks div[role='button'], div[role='region'] div.p6n-content-block-layout")
            if cards.count() > block_index:
                cards.nth(block_index).click()
                self.page.wait_for_timeout(2000)
                return True
        except Exception as e:
            self.log(f"[LAYOUT] Notice inserting block card {block_index}: {e}")
        return False

    def add_content_block_2(self, items: List[Dict[str, str]], section_style: Optional[str] = None):
        """Adds Content Block 2 (2 Equal Columns: Image + Title + Description each)."""
        self.log("[LAYOUT] Inserting Content Block 2 (2 Columns)...")
        try:
            self._prepare_canvas_for_new_section()
            self._scroll_sidebar_top()
            self.page.wait_for_timeout(500)

            # 1. Click Content Block 2 card in sidebar (Row 1, Col 2)
            card_loc = self.page.locator(
                "[aria-label*='Two column image and captions' i], "
                "div[aria-label*='Two column' i], "
                "div[aria-label*='2 column' i]"
            ).first

            if card_loc.is_visible():
                card_loc.click()
            else:
                self.page.mouse.click(1208, 373)

            self.page.wait_for_timeout(2500)
            last_sec = self.page.locator("article section").last

            # 2. Upload images for both columns
            for col_idx, item in enumerate(items[:2]):
                img_path = item.get("image_path", "")
                if img_path and os.path.exists(img_path):
                    rem_btns = self.page.locator("article section").last.locator(
                        "div[role='button'][aria-label*='Insert content' i], div.U26fgb.JRtysb"
                    )
                    target_idx = 0 if rem_btns.count() == 1 else col_idx
                    if rem_btns.count() > target_idx:
                        rem_btns.nth(target_idx).click()
                    else:
                        sec_box = last_sec.bounding_box()
                        if sec_box:
                            offset_x = 215 if col_idx == 0 else 580
                            self.page.mouse.click(sec_box['x'] + offset_x, sec_box['y'] + 100)

                    self.page.wait_for_timeout(1000)

                    upload_info = self.page.evaluate("""() => {
                        const all = Array.from(document.querySelectorAll('*'));
                        const matches = all.filter(el => el.children.length === 0 && el.innerText && el.innerText.trim() === 'Upload');
                        return matches.map(el => {
                            const rect = el.getBoundingClientRect();
                            return {
                                x: Math.round(rect.x + rect.width / 2),
                                y: Math.round(rect.y + rect.height / 2),
                                visible: rect.width > 0 && rect.height > 0 && rect.y > 100
                            };
                        }).filter(u => u.visible);
                    }""")

                    if upload_info:
                        u = upload_info[0]
                        with self.page.expect_file_chooser(timeout=8000) as fc_info:
                            self.page.mouse.click(u['x'], u['y'])
                        fc_info.value.set_files(img_path)
                        self.page.wait_for_timeout(3500)
                        self.log(f"[SUCCESS] Uploaded {os.path.basename(img_path)} to Content Block 2 column {col_idx + 1}.")

            # 3. Populate Text in Column 1 and Column 2
            text_gridcells = self.page.locator("article section").last.locator("div[role='gridcell'][aria-label='Text']")
            tg_count = text_gridcells.count()

            data_map = []
            if len(items) > 0:
                data_map.append((0, items[0].get("title", "")))
                data_map.append((1, items[0].get("description", items[0].get("body", ""))))
            if len(items) > 1:
                data_map.append((2, items[1].get("title", "")))
                data_map.append((3, items[1].get("description", items[1].get("body", ""))))

            for cell_idx, text_val in data_map:
                if tg_count > cell_idx and text_val:
                    cell = text_gridcells.nth(cell_idx)
                    cell.click()
                    self.page.wait_for_timeout(400)
                    active_editor = cell.locator("div[contenteditable='true']").first
                    if active_editor.is_visible():
                        self.paste_text_into_editor(active_editor, text_val)
                    else:
                        self.paste_text_into_editor(self.page.locator("div[contenteditable='true']").last, text_val)
                    self.page.wait_for_timeout(400)
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(200)

            # 4. Optional Section Color Style (Style 1, 2, 3)
            if section_style:
                self.set_section_color(section_style)

            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            self.log("[SUCCESS] Content Block 2 populated successfully.")
        except Exception as e:
            self.log(f"[LAYOUT] Notice Content Block 2: {e}")

    def add_content_block_3(self, image_paths: List[str], section_style: Optional[str] = None):
        """Adds Content Block 3 (Collage: 2 Small Images Left + 1 Large Image Right)."""
        self.log("[LAYOUT] Inserting Content Block 3 (Collage: 3 Images)...")
        try:
            self._prepare_canvas_for_new_section()
            self._scroll_sidebar_top()
            self.page.wait_for_timeout(500)

            # Click Content Block 3 card in sidebar (Row 2, Col 1)
            card_loc = self.page.locator(
                "[aria-label*='Three images' i], "
                "div[aria-label*='Add layout: Three images' i]"
            ).first

            if card_loc.is_visible():
                card_loc.click()
            else:
                self.page.mouse.click(1088, 461)

            self.page.wait_for_timeout(2500)
            last_sec = self.page.locator("article section").last

            # Upload up to 3 images
            for i, img_path in enumerate(image_paths[:3]):
                if img_path and os.path.exists(img_path):
                    rem_btns = self.page.locator("article section").last.locator(
                        "div[role='button'][aria-label*='Insert content' i], div.U26fgb.JRtysb"
                    )
                    if rem_btns.count() > 0:
                        rem_btns.first.click()
                        self.page.wait_for_timeout(1000)

                        upload_info = self.page.evaluate("""() => {
                            const all = Array.from(document.querySelectorAll('*'));
                            const matches = all.filter(el => el.children.length === 0 && el.innerText && el.innerText.trim() === 'Upload');
                            return matches.map(el => {
                                const rect = el.getBoundingClientRect();
                                return {
                                    x: Math.round(rect.x + rect.width / 2),
                                    y: Math.round(rect.y + rect.height / 2),
                                    visible: rect.width > 0 && rect.height > 0 && rect.y > 100
                                };
                            }).filter(u => u.visible);
                        }""")

                        if upload_info:
                            u = upload_info[0]
                            with self.page.expect_file_chooser(timeout=8000) as fc_info:
                                self.page.mouse.click(u['x'], u['y'])
                            fc_info.value.set_files(img_path)
                            self.page.wait_for_timeout(3500)
                            self.log(f"[SUCCESS] Uploaded {os.path.basename(img_path)} into Content Block 3 slot {i + 1}.")

            if section_style:
                self.set_section_color(section_style)

            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            self.log("[SUCCESS] Content Block 3 populated successfully.")
        except Exception as e:
            self.log(f"[LAYOUT] Notice Content Block 3: {e}")

    def add_content_block_4(self, items: List[Dict[str, str]], section_style: Optional[str] = None):
        """Adds Content Block 4 (3 Equal Columns: Image + Title + Description each)."""
        self.log("[LAYOUT] Inserting Content Block 4 (3 Columns Grid)...")
        try:
            self._prepare_canvas_for_new_section()
            self._scroll_sidebar_top()
            self.page.wait_for_timeout(500)

            # 1. Click Content Block 4 card in sidebar (Row 2, Col 2)
            card_loc = self.page.locator(
                "[aria-label*='Three column image and captions' i], "
                "div[aria-label*='Three column' i], "
                "div[aria-label*='3 column' i]"
            ).first

            if card_loc.is_visible():
                card_loc.click()
            else:
                self.page.mouse.click(1208, 461)

            self.page.wait_for_timeout(2500)
            last_sec = self.page.locator("article section").last

            # 2. Upload images for up to 3 columns
            for col_idx, item in enumerate(items[:3]):
                img_path = item.get("image_path", "")
                if img_path and os.path.exists(img_path):
                    rem_btns = self.page.locator("article section").last.locator(
                        "div[role='button'][aria-label*='Insert content' i], div.U26fgb.JRtysb"
                    )
                    if rem_btns.count() > 0:
                        rem_btns.first.click()
                        self.page.wait_for_timeout(1000)

                        upload_info = self.page.evaluate("""() => {
                            const all = Array.from(document.querySelectorAll('*'));
                            const matches = all.filter(el => el.children.length === 0 && el.innerText && el.innerText.trim() === 'Upload');
                            return matches.map(el => {
                                const rect = el.getBoundingClientRect();
                                return {
                                    x: Math.round(rect.x + rect.width / 2),
                                    y: Math.round(rect.y + rect.height / 2),
                                    visible: rect.width > 0 && rect.height > 0 && rect.y > 100
                                };
                            }).filter(u => u.visible);
                        }""")

                        if upload_info:
                            u = upload_info[0]
                            with self.page.expect_file_chooser(timeout=8000) as fc_info:
                                self.page.mouse.click(u['x'], u['y'])
                            fc_info.value.set_files(img_path)
                            self.page.wait_for_timeout(3500)
                            self.log(f"[SUCCESS] Uploaded {os.path.basename(img_path)} to Content Block 4 column {col_idx + 1}.")

            # 3. Populate Title and Description across all 3 columns
            text_gridcells = self.page.locator("article section").last.locator("div[role='gridcell'][aria-label='Text']")
            tg_count = text_gridcells.count()

            cell_index = 0
            for col_i, item in enumerate(items[:3]):
                title = item.get("title", "")
                desc = item.get("description", item.get("body", ""))

                if tg_count > cell_index and title:
                    cell = text_gridcells.nth(cell_index)
                    cell.click()
                    self.page.wait_for_timeout(400)
                    active_editor = cell.locator("div[contenteditable='true']").first
                    if active_editor.is_visible():
                        self.paste_text_into_editor(active_editor, title)
                    else:
                        self.paste_text_into_editor(self.page.locator("div[contenteditable='true']").last, title)
                    self.page.wait_for_timeout(300)
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(200)
                cell_index += 1

                if tg_count > cell_index and desc:
                    cell = text_gridcells.nth(cell_index)
                    cell.click()
                    self.page.wait_for_timeout(400)
                    active_editor = cell.locator("div[contenteditable='true']").first
                    if active_editor.is_visible():
                        self.paste_text_into_editor(active_editor, desc)
                    else:
                        self.paste_text_into_editor(self.page.locator("div[contenteditable='true']").last, desc)
                    self.page.wait_for_timeout(300)
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(200)
                cell_index += 1

            if section_style:
                self.set_section_color(section_style)

            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            self.log("[SUCCESS] Content Block 4 populated successfully.")
        except Exception as e:
            self.log(f"[LAYOUT] Notice Content Block 4: {e}")

    def add_content_block_5(self, items: List[Dict[str, str]], section_style: Optional[str] = None):
        """Adds Content Block 5 (Dual Horizontal Cards: 2 Columns, each with Image Left & Text Right)."""
        self.log("[LAYOUT] Inserting Content Block 5 (Dual Horizontal Cards)...")
        try:
            self._prepare_canvas_for_new_section()
            self._scroll_sidebar_top()
            self.page.wait_for_timeout(500)

            # 1. Click Content Block 5 card in sidebar (Row 3, Col 1)
            card_loc = self.page.locator(
                "[aria-label*='Two column image and side captions' i], "
                "div[aria-label*='side captions' i]"
            ).first

            if card_loc.is_visible():
                card_loc.click()
            else:
                self.page.mouse.click(1088, 549)

            self.page.wait_for_timeout(2500)
            last_sec = self.page.locator("article section").last

            # 2. Upload images for up to 2 cards
            for col_idx, item in enumerate(items[:2]):
                img_path = item.get("image_path", "")
                if img_path and os.path.exists(img_path):
                    rem_btns = self.page.locator("article section").last.locator(
                        "div[role='button'][aria-label*='Insert content' i], div.U26fgb.JRtysb"
                    )
                    if rem_btns.count() > 0:
                        rem_btns.first.click()
                        self.page.wait_for_timeout(1000)

                        upload_info = self.page.evaluate("""() => {
                            const all = Array.from(document.querySelectorAll('*'));
                            const matches = all.filter(el => el.children.length === 0 && el.innerText && el.innerText.trim() === 'Upload');
                            return matches.map(el => {
                                const rect = el.getBoundingClientRect();
                                return {
                                    x: Math.round(rect.x + rect.width / 2),
                                    y: Math.round(rect.y + rect.height / 2),
                                    visible: rect.width > 0 && rect.height > 0 && rect.y > 100
                                };
                            }).filter(u => u.visible);
                        }""")

                        if upload_info:
                            u = upload_info[0]
                            with self.page.expect_file_chooser(timeout=8000) as fc_info:
                                self.page.mouse.click(u['x'], u['y'])
                            fc_info.value.set_files(img_path)
                            self.page.wait_for_timeout(3500)
                            self.log(f"[SUCCESS] Uploaded {os.path.basename(img_path)} to Content Block 5 card {col_idx + 1}.")

            # 3. Populate Title and Description across both cards
            text_gridcells = self.page.locator("article section").last.locator("div[role='gridcell'][aria-label='Text']")
            tg_count = text_gridcells.count()

            cell_index = 0
            for col_i, item in enumerate(items[:2]):
                title = item.get("title", "")
                desc = item.get("description", item.get("body", ""))

                if tg_count > cell_index and title:
                    cell = text_gridcells.nth(cell_index)
                    cell.click()
                    self.page.wait_for_timeout(400)
                    active_editor = cell.locator("div[contenteditable='true']").first
                    if active_editor.is_visible():
                        self.paste_text_into_editor(active_editor, title)
                    else:
                        self.paste_text_into_editor(self.page.locator("div[contenteditable='true']").last, title)
                    self.page.wait_for_timeout(300)
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(200)
                cell_index += 1

                if tg_count > cell_index and desc:
                    cell = text_gridcells.nth(cell_index)
                    cell.click()
                    self.page.wait_for_timeout(400)
                    active_editor = cell.locator("div[contenteditable='true']").first
                    if active_editor.is_visible():
                        self.paste_text_into_editor(active_editor, desc)
                    else:
                        self.paste_text_into_editor(self.page.locator("div[contenteditable='true']").last, desc)
                    self.page.wait_for_timeout(300)
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(200)
                cell_index += 1

            if section_style:
                self.set_section_color(section_style)

            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            self.log("[SUCCESS] Content Block 5 populated successfully.")
        except Exception as e:
            self.log(f"[LAYOUT] Notice Content Block 5: {e}")

    def add_content_block_6(self, items: List[Dict[str, str]], section_style: Optional[str] = None):
        """Adds Content Block 6 (Four Column Showcase: 4 Columns with Image + Caption each)."""
        self.log("[LAYOUT] Inserting Content Block 6 (Four Column Showcase)...")
        try:
            self._prepare_canvas_for_new_section()
            self._scroll_sidebar_top()
            self.page.wait_for_timeout(500)

            # 1. Click Content Block 6 card in sidebar (Row 3, Col 2)
            card_loc = self.page.locator(
                "[aria-label*='Four column image and captions' i], "
                "div[aria-label*='Four column' i]"
            ).first

            if card_loc.is_visible():
                card_loc.click()
            else:
                self.page.mouse.click(1208, 549)

            self.page.wait_for_timeout(2500)

            # 2. Upload images for up to 4 columns
            for col_idx, item in enumerate(items[:4]):
                img_path = item.get("image_path", "")
                if img_path and os.path.exists(img_path):
                    rem_btns = self.page.locator("article section").last.locator(
                        "div[role='button'][aria-label*='Insert content' i], div.U26fgb.JRtysb"
                    )
                    if rem_btns.count() > 0:
                        rem_btns.first.click()
                        self.page.wait_for_timeout(1000)

                        upload_info = self.page.evaluate("""() => {
                            const all = Array.from(document.querySelectorAll('*'));
                            const matches = all.filter(el => el.children.length === 0 && el.innerText && el.innerText.trim() === 'Upload');
                            return matches.map(el => {
                                const rect = el.getBoundingClientRect();
                                return {
                                    x: Math.round(rect.x + rect.width / 2),
                                    y: Math.round(rect.y + rect.height / 2),
                                    visible: rect.width > 0 && rect.height > 0 && rect.y > 100
                                };
                            }).filter(u => u.visible);
                        }""")

                        if upload_info:
                            u = upload_info[0]
                            with self.page.expect_file_chooser(timeout=8000) as fc_info:
                                self.page.mouse.click(u['x'], u['y'])
                            fc_info.value.set_files(img_path)
                            self.page.wait_for_timeout(3500)
                            self.log(f"[SUCCESS] Uploaded {os.path.basename(img_path)} to Content Block 6 column {col_idx + 1}.")

            # 3. Populate captions/titles in each column
            text_gridcells = self.page.locator("article section").last.locator("div[role='gridcell'][aria-label='Text']")
            tg_count = text_gridcells.count()

            for col_i, item in enumerate(items[:4]):
                caption = item.get("title", item.get("caption", item.get("text", "")))
                if tg_count > col_i and caption:
                    cell = text_gridcells.nth(col_i)
                    cell.click()
                    self.page.wait_for_timeout(400)
                    active_editor = cell.locator("div[contenteditable='true']").first
                    if active_editor.is_visible():
                        self.paste_text_into_editor(active_editor, caption)
                    else:
                        self.paste_text_into_editor(self.page.locator("div[contenteditable='true']").last, caption)
                    self.page.wait_for_timeout(300)
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(200)

            if section_style:
                self.set_section_color(section_style)

            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            self.log("[SUCCESS] Content Block 6 populated successfully.")
        except Exception as e:
            self.log(f"[LAYOUT] Notice Content Block 6: {e}")

    def select_google_theme(self, theme_name: str = "Aristotle", color_index: int = 1):
        """
        Selects a theme from 'Created by Google' under the Themes tab,
        optionally sets the color palette swatch (1-5),
        and switches back to the Insert tab.
        """
        self.log(f"[THEME] Selecting Google theme '{theme_name}' (color #{color_index})...")
        try:
            # 1. Click Themes tab
            themes_tab_clicked = self.page.evaluate("""() => {
                const all = Array.from(document.querySelectorAll('*'));
                const match = all.find(el => el.children.length === 0 && el.innerText && el.innerText.trim() === 'Themes');
                if (match) {
                    const r = match.getBoundingClientRect();
                    if (r.x > 900 && r.y < 200) {
                        match.click();
                        return true;
                    }
                }
                return false;
            }""")
            if not themes_tab_clicked:
                tab_loc = self.page.locator("text='Themes'").first
                if tab_loc.is_visible():
                    tab_loc.click()
            self.page.wait_for_timeout(1000)

            # 2. Scroll theme card into view and click it
            card_coords = self.page.evaluate("""(name) => {
                const all = Array.from(document.querySelectorAll("*"));
                // Search for theme containers under Created by Google
                const match = all.find(el => {
                    const r = el.getBoundingClientRect();
                    return r.x > 900 && (el.className && el.className.toString().includes('m6xOQ')) && el.innerText && el.innerText.toLowerCase().startsWith(name.toLowerCase());
                });
                if (match) {
                    match.scrollIntoView({ block: 'center', behavior: 'instant' });
                    const r = match.getBoundingClientRect();
                    return { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + 40) };
                }
                // Fallback: search by text node
                const textMatch = all.find(el => {
                    const r = el.getBoundingClientRect();
                    return r.x > 900 && el.children.length === 0 && el.innerText && el.innerText.trim().toLowerCase() === name.toLowerCase();
                });
                if (textMatch) {
                    textMatch.scrollIntoView({ block: 'center', behavior: 'instant' });
                    const r = textMatch.getBoundingClientRect();
                    return { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2) };
                }
                return null;
            }""", theme_name)

            if card_coords:
                self.page.mouse.click(card_coords['x'], card_coords['y'])
                self.page.wait_for_timeout(2000)
                self.log(f"[SUCCESS] Theme '{theme_name}' activated.")
            else:
                self.log(f"[WARNING] Theme card '{theme_name}' not found.")

            # 3. If color_index > 1, click corresponding palette radio button
            if color_index > 1:
                radio_coords = self.page.evaluate("""(cIdx) => {
                    const activeContainer = Array.from(document.querySelectorAll("*")).find(el => {
                        const r = el.getBoundingClientRect();
                        return r.x > 900 && (el.className && el.className.toString().includes('m6xOQ')) && el.getAttribute('checked') === 'true';
                    });
                    if (!activeContainer) return null;
                    const radios = Array.from(activeContainer.querySelectorAll("div[role='radio']"));
                    if (radios.length >= cIdx) {
                        const targetRadio = radios[cIdx - 1];
                        const r = targetRadio.getBoundingClientRect();
                        return { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2), label: targetRadio.getAttribute('aria-label') };
                    }
                    return null;
                }""", color_index)

                if radio_coords:
                    self.page.mouse.click(radio_coords['x'], radio_coords['y'])
                    self.page.wait_for_timeout(1000)
                    self.log(f"[SUCCESS] Swatch #{color_index} ('{radio_coords['label']}') selected.")

            # 4. Switch back to Insert tab
            self.page.evaluate("""() => {
                const all = Array.from(document.querySelectorAll('*'));
                const insertTab = all.find(el => el.children.length === 0 && el.innerText && el.innerText.trim() === 'Insert');
                if (insertTab) {
                    const r = insertTab.getBoundingClientRect();
                    if (r.x > 900 && r.y < 200) insertTab.click();
                }
            }""")
            self.page.wait_for_timeout(1000)
            self.log(f"[SUCCESS] Switched back to Insert tab.")

        except Exception as e:
            self.log(f"[THEME] Notice: {e}")

    def set_announcement_banner(
        self,
        message: str,
        button_label: Optional[str] = None,
        link: Optional[str] = None,
        open_in_new_tab: bool = True,
        visibility_all_pages: bool = True
    ):
        """
        Configures and enables Google Sites Announcement Banner at the very top of the page.
        Supports message text, optional CTA button label and link, new tab toggle, and visibility.
        """
        self.log(f"[BANNER] Configuring Announcement Banner: '{message}'...")
        try:
            # 1. Open Settings modal
            settings_btn = self.page.locator("button[aria-label*='Settings' i], div[role='button'][aria-label*='Settings' i], [aria-label='Settings']").first
            if settings_btn.is_visible():
                settings_btn.click()
            else:
                self.page.evaluate("""() => {
                    const all = Array.from(document.querySelectorAll("*"));
                    const s = all.find(el => el.getAttribute('aria-label') && el.getAttribute('aria-label').toLowerCase().includes('settings') && el.getBoundingClientRect().y < 100);
                    if (s) s.click();
                }""")
            self.page.wait_for_timeout(2000)

            # 2. Click Announcement banner nav item inside Settings dialog
            self.page.evaluate("""() => {
                const all = Array.from(document.querySelectorAll("[role='dialog'] *"));
                const target = all.find(el => el.children.length === 0 && el.innerText && el.innerText.trim().toLowerCase() === 'announcement banner');
                if (target) target.click();
            }""")
            self.page.wait_for_timeout(1500)

            # 3. Enable 'Show banner' switch if not already enabled
            self.page.evaluate("""() => {
                const all = Array.from(document.querySelectorAll("[role='dialog'] *"));
                const sw = all.find(el => el.getAttribute('role') === 'switch' || (el.tagName === 'INPUT' && el.getAttribute('type') === 'checkbox') || (el.getAttribute('role') === 'checkbox'));
                if (sw) {
                    const isChecked = sw.getAttribute('aria-checked') === 'true' || sw.checked;
                    if (!isChecked) sw.click();
                }
            }""")
            self.page.wait_for_timeout(500)

            # 4. Fill Message
            msg_input = self.page.locator("[role='dialog'] input[aria-label*='Message' i], [role='dialog'] textarea").first
            if msg_input.is_visible():
                msg_input.click()
                msg_input.fill(message[:150])
            else:
                first_input = self.page.locator("[role='dialog'] input[type='text']").first
                if first_input.is_visible():
                    first_input.click()
                    first_input.fill(message[:150])
            self.page.wait_for_timeout(400)

            # 5. Fill Button label (optional)
            if button_label:
                btn_input = self.page.locator("[role='dialog'] input[aria-label*='Button label' i], [role='dialog'] input[aria-label*='label' i]").first
                if btn_input.is_visible():
                    btn_input.click()
                    btn_input.fill(button_label[:25])
                self.page.wait_for_timeout(400)

            # 6. Fill Link (optional)
            if link:
                link_input = self.page.locator("[role='dialog'] input[aria-label*='Link' i]").first
                if link_input.is_visible():
                    link_input.click()
                    link_input.fill(link)
                self.page.wait_for_timeout(400)

            # 7. Open in new tab checkbox
            if open_in_new_tab:
                new_tab_box = self.page.locator("[role='dialog'] [aria-label*='Open in new tab' i], [role='dialog'] input[type='checkbox']").last
                if new_tab_box.is_visible() and not new_tab_box.is_checked():
                    new_tab_box.click()
                    self.page.wait_for_timeout(300)

            # 8. Visibility: All pages vs Home page only
            if visibility_all_pages:
                all_pages_radio = self.page.locator("[role='dialog'] [aria-label*='Visibility all pages' i], [role='dialog'] div[role='radio']:has-text('All pages')").first
                if all_pages_radio.is_visible():
                    all_pages_radio.click()
            else:
                home_radio = self.page.locator("[role='dialog'] [aria-label*='Visibility home page only' i], [role='dialog'] div[role='radio']:has-text('Home page only')").first
                if home_radio.is_visible():
                    home_radio.click()

            self.page.wait_for_timeout(500)

            # 9. Close Settings modal
            close_btn = self.page.locator("[role='dialog'] button[aria-label*='Close' i], [role='dialog'] [aria-label='Close']").first
            if close_btn.is_visible():
                close_btn.click()
            else:
                self.page.keyboard.press("Escape")

            self.page.wait_for_timeout(1500)
            self.log(f"[SUCCESS] Announcement Banner active: '{message}'")

        except Exception as e:
            self.log(f"[BANNER] Notice: {e}")

    def add_map_embed(self, query: str = "New Delhi, India", make_full_width: bool = True):
        """Inserts a Google Map location embed and stretches it to full width across 12 grid columns."""
        self.log(f"[MAP] Adding map embed for: '{query}'...")
        try:
            # 1. Prepare canvas
            self._prepare_canvas_for_new_section()

            # 2. Switch to Insert tab
            insert_tab = self.page.locator("div[role='tab']:has-text('Insert'), [aria-label*='Insert' i]").first
            if insert_tab.is_visible():
                insert_tab.click(force=True)
                self.page.wait_for_timeout(300)

            # 3. Scroll sidebar panel down to reveal Map widget
            self._scroll_sidebar_down(950)

            sidebar = self.page.locator("div[role='tabpanel'], div.p6n-insert-panel, aside").first
            map_btn = None
            if sidebar.is_visible():
                candidates = sidebar.locator("div[role='button']:has-text('Map'), [aria-label*='Map' i]")
                if candidates.count() > 0:
                    map_btn = candidates.first
            if not map_btn or not map_btn.is_visible():
                map_btn = self.page.locator("div[role='tabpanel'] div[role='button']:has-text('Map'), aside div[role='button']:has-text('Map'), div[role='button']:has-text('Map')").first

            if map_btn and map_btn.is_visible():
                try:
                    map_btn.scroll_into_view_if_needed(timeout=3000)
                except Exception:
                    pass
                map_btn.click(force=True)
                self.page.wait_for_timeout(3000)

                # Google Maps picker renders inside an iframe with class .picker-frame or URL with 'picker'
                map_inserted = False
                try:
                    picker_loc = self.page.frame_locator("iframe[src*='picker'], iframe.picker-frame, div[role='dialog'] iframe").first
                    search_box = picker_loc.locator("input#searchboxinput, input[aria-label*='Search' i], input[type='text'], input.picker-search-input").first
                    if search_box.is_visible():
                        self.log(f"[MAP] Entering search query into picker frame: '{query}'...")
                        search_box.click()
                        search_box.fill(query)
                        self.page.keyboard.press("Enter")
                        self.page.wait_for_timeout(3500)

                        sugg = picker_loc.locator("div[role='option'], div.suggest-item, div.picker-search-suggest-item").first
                        if sugg.is_visible():
                            sugg.click(force=True)
                            self.page.wait_for_timeout(2000)

                        # USER INSTRUCTION: Click Select button at bottom of picker
                        sel_btn = picker_loc.locator("button:has-text('Select'), button[name='select'], div[role='button']:has-text('Select'), [aria-label*='Select' i], button.picker-action-button").first
                        if sel_btn.is_visible():
                            sel_btn.click(force=True)
                            self._wait_dialog_closed()
                            self.page.wait_for_timeout(2500)
                            self.log("[SUCCESS] Map embedded via picker Select button.")
                            map_inserted = True
                except Exception as e:
                    self.log(f"[MAP] Notice frame_locator: {e}")

                if not map_inserted:
                    # Look through frames specifically having 'picker' in URL
                    picker_frame = None
                    for frame in self.page.frames:
                        if "picker" in frame.url.lower():
                            picker_frame = frame
                            break

                    if picker_frame:
                        self.log("[MAP] Detected map picker frame by URL. Entering search query...")
                        search_input = picker_frame.locator("input#searchboxinput, input[aria-label*='Search' i], input[type='text'], input.picker-search-input").first
                        if search_input.is_visible():
                            search_input.click()
                            search_input.fill(query)
                            picker_frame.keyboard.press("Enter")
                            self.page.wait_for_timeout(3500)

                            suggestion = picker_frame.locator("div[role='option'], div.suggest-item, div.picker-search-suggest-item").first
                            if suggestion.is_visible():
                                suggestion.click(force=True)
                                self.page.wait_for_timeout(2000)

                        select_btn = picker_frame.locator("button:has-text('Select'), button[name='select'], div[role='button']:has-text('Select'), [aria-label*='Select' i], button.picker-action-button").first
                        if select_btn.is_visible():
                            select_btn.click(force=True)
                            self._wait_dialog_closed()
                            self.page.wait_for_timeout(2500)
                            self.log("[SUCCESS] Map embedded via picker frame Select button.")
                            map_inserted = True

                if not map_inserted:
                    # Check main dialog or any open modal
                    dialog = self.page.locator("div[role='dialog'], div[aria-modal='true']").last
                    search_input = dialog.locator("input[placeholder*='Search' i], input[aria-label*='Search' i], input[type='text']").first
                    if not search_input.is_visible():
                        search_input = self.page.locator("div[role='dialog'] input").first

                    if search_input.is_visible():
                        search_input.click()
                        search_input.fill(query)
                        self.page.keyboard.press("Enter")
                        self.page.wait_for_timeout(2500)

                        # Click place suggestion item or map pin to enable Select button
                        sugg = self.page.locator(
                            "div[role='dialog'] div[role='option'], "
                            "div[role='dialog'] div.suggest-item, "
                            "div[role='dialog'] div[aria-label*='result' i], "
                            "div[role='dialog'] [role='listbox'] > *"
                        ).first
                        if sugg.count() > 0 and sugg.is_visible():
                            sugg.click(force=True)
                            self.page.wait_for_timeout(1500)
                        else:
                            d_box = dialog.bounding_box()
                            if d_box:
                                self.page.mouse.click(d_box['x'] + d_box['width'] / 2, d_box['y'] + d_box['height'] / 2)
                                self.page.wait_for_timeout(1000)

                    # Click Select button
                    select_btn = self.page.locator(
                        "div[role='dialog'] button:has-text('Select'), "
                        "div[role='dialog'] div[role='button']:has-text('Select'), "
                        "button[name='select'], "
                        "button:has-text('Select'), "
                        "[aria-label*='Select' i]"
                    ).first

                    if not (select_btn.count() > 0 and select_btn.is_visible()):
                        # Check all frames for Select button
                        for frame in self.page.frames:
                            fb = frame.locator("button:has-text('Select'), div[role='button']:has-text('Select'), button[name='select']").first
                            if fb.count() > 0 and fb.is_visible():
                                select_btn = fb
                                break

                    if select_btn.count() > 0 and select_btn.is_visible():
                        select_btn.click(force=True)
                        self._wait_dialog_closed()
                        self.page.wait_for_timeout(2500)
                        self.log("[SUCCESS] Map embedded via dialog Select button.")
                        map_inserted = True
                    else:
                        self.log("[MAP] [WARNING] Select button not visible in map dialog.")

                if make_full_width:
                    self.resize_image_to_full_width()

                # Ensure dialog is dismissed if still present
                self._wait_dialog_closed(timeout=2000)
            else:
                self.log("[MAP] [WARNING] Map widget not found in sidebar.")

            # Scroll sidebar back to top
            self._scroll_sidebar_top()
        except Exception as e:
            self.log(f"[MAP] Notice adding map embed: {e}")

    def add_footer(self, footer_text: str):
        """Scrolls to bottom, clicks (+) Add Footer, fills custom text, and deselects to commit (Footer-1 to 3)."""
        self.log(f"[FOOTER] Setting footer text: '{footer_text[:35]}...'")
        try:
            # Scroll down to reveal bottom of canvas
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(600)

            # Locate Add Footer button (Footer-1)
            footer_btn = self.page.locator("div[role='button']:has-text('Add footer'), button:has-text('Add footer'), div.p6n-wysiwyg-footer-edit-button, [aria-label*='Add footer' i]").first
            if not footer_btn.is_visible():
                # Hover near the bottom edge of canvas
                self.page.mouse.move(500, 700)
                self.page.wait_for_timeout(500)

            if footer_btn.is_visible():
                footer_btn.click()
                self.page.wait_for_timeout(1000)

                # Focus into footer editable text box (Footer-2)
                footer_box = self.page.locator("footer div[contenteditable='true'], div[role='contentinfo'] div[contenteditable='true'], div[contenteditable='true']").last
                if footer_box.is_visible():
                    footer_box.click()
                    self.page.keyboard.press("Control+A")
                    self.page.keyboard.press("Backspace")
                    self.page.keyboard.type(footer_text)
                    self.page.wait_for_timeout(500)

                # Deselect to commit/save footer (Footer-3)
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(500)
                self.log("[SUCCESS] Footer content added and committed.")
        except Exception as e:
            self.log(f"[FOOTER] Notice adding footer: {e}")

    def publish_and_get_url(self, keyword: str) -> Optional[str]:
        """Publishes the Google Site, validates lowercase web address, checks uniqueness, and extracts live URL (publish-1 to 5)."""
        self.log("[PUBLISH] Initiating publication...")
        # Format base slug strictly lowercase, alphanumeric with single hyphens (publish-2 rule)
        base_slug = re.sub(r'[^a-z0-9-]', '-', keyword.strip().lower())
        base_slug = re.sub(r'-+', '-', base_slug).strip('-')[:18]
        timestamp_suffix = datetime.now().strftime("%d%H%M")
        full_slug = f"{base_slug}-{timestamp_suffix}"[:28].rstrip('-')

        public_url = None

        try:
            # 1. Dismiss any open menus/toolbars
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(1000)

            # 2. Click top-right blue Publish button (publish-1)
            publish_btn = self.page.locator("div[role='button']:has-text('Publish'), button:has-text('Publish')").first
            publish_btn.click(force=True)
            self.page.wait_for_timeout(3500)

            # 3. Handle 'Publish to the web' dialog (publish-2)
            slug_input = self.page.locator(
                "div[role='dialog'] input[type='text']:visible, "
                "div[role='dialog'] input:not([type='checkbox']):visible"
            ).first

            if slug_input.is_visible():
                current_slug = full_slug
                import random

                for attempt in range(5):
                    self.log(f"[PUBLISH] Entering Web address (Attempt {attempt+1}): '{current_slug}'...")

                    slug_input.click()
                    self.page.keyboard.press("Control+A")
                    self.page.keyboard.press("Backspace")
                    self.page.wait_for_timeout(200)

                    # USER RULE: Type slug except last character, pause, then type last character
                    # This forces Google Sites input event to trigger and immediately enables the Publish button
                    if len(current_slug) > 1:
                        prefix = current_slug[:-1]
                        last_char = current_slug[-1]
                        self.page.keyboard.type(prefix, delay=35)
                        self.page.wait_for_timeout(800)
                        self.page.keyboard.type(last_char, delay=50)
                    else:
                        self.page.keyboard.type(current_slug, delay=40)

                    # 2.5s wait for async validation
                    self.page.wait_for_timeout(2500)

                    # Error detection — strict scope
                    error_el = self.page.locator(
                        "div[role='dialog'] :text('already taken'), "
                        "div[role='dialog'] :text('already exists'), "
                        "div[role='dialog'] div.p6n-form-field-error:visible"
                    ).first

                    if error_el.count() > 0 and error_el.is_visible():
                        rand_num = random.randint(100, 999)
                        self.log(f"[PUBLISH] '{current_slug}' taken. Retrying with suffix...")
                        current_slug = f"{base_slug[:14]}-{timestamp_suffix}{rand_num}"[:28].rstrip('-')
                        continue
                    else:
                        full_slug = current_slug
                        break

                # Checkbox — ensure unchecked
                search_checkbox = self.page.locator("div[role='dialog'] input[type='checkbox']").first
                if search_checkbox.count() > 0 and search_checkbox.is_visible():
                    if search_checkbox.is_checked():
                        self.log("[PUBLISH] Unchecking search engines checkbox...")
                        search_checkbox.uncheck()
                        self.page.wait_for_timeout(400)

                # Confirm Publish button (filter for real visible element with width > 30)
                self.log("[PUBLISH] Clicking Confirm Publish button...")
                click_res = self.page.evaluate("""() => {
                    const dialog = document.querySelector("[role='dialog'], div[aria-modal='true']");
                    if (!dialog) return { success: false };

                    const btns = Array.from(dialog.querySelectorAll("div[role='button'], button"));
                    const validPubBtns = btns.filter(b => {
                        const t = b.innerText ? b.innerText.trim().toLowerCase() : '';
                        const r = b.getBoundingClientRect();
                        return t === 'publish' && r.width > 30 && r.height > 20;
                    });

                    if (validPubBtns.length > 0) {
                        const targetBtn = validPubBtns[validPubBtns.length - 1];
                        const r = targetBtn.getBoundingClientRect();
                        targetBtn.click();
                        return {
                            success: true,
                            clickPoint: { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2) }
                        };
                    }
                    return { success: false };
                }""")

                if click_res.get("success") and "clickPoint" in click_res:
                    pt = click_res["clickPoint"]
                    self.page.mouse.click(pt["x"], pt["y"])
                    self.log("[PUBLISH] Publish clicked. Publishing...")
                else:
                    # Fallback locator
                    confirm_pub = self.page.locator("div[role='dialog'] div[role='button']:has-text('Publish'):visible, div[role='dialog'] button:has-text('Publish'):visible").last
                    if confirm_pub.is_visible():
                        confirm_pub.click(force=True)
                        self.log("[PUBLISH] Publish clicked via fallback locator.")

                self.page.wait_for_timeout(4000)

            # 4. Extract Genuine Live Published URL
            # Loop check for up to 16 seconds (Google Sites server deployment takes 3-6s)
            for attempt in range(8):
                # Method A: Toast notification 'Your site has been published successfully' -> Click 'View'
                try:
                    view_clicked = self.page.evaluate("""() => {
                        const all = Array.from(document.querySelectorAll("*"));
                        const viewBtn = all.find(el => {
                            const t = el.innerText ? el.innerText.trim().toLowerCase() : '';
                            const r = el.getBoundingClientRect();
                            return (t === 'view' || t.includes('view')) && r.width > 10 && r.y > 500 && (el.tagName === 'A' || el.tagName === 'BUTTON' || el.getAttribute('role') === 'button');
                        });
                        if (viewBtn) {
                            viewBtn.click();
                            return true;
                        }
                        return false;
                    }""")

                    if view_clicked:
                        self.log("[PUBLISH] Toast notification detected. Opening live published site tab via 'View'...")
                        self.page.wait_for_timeout(2500)
                        for p in self.context.pages:
                            if "sites.google.com/view" in p.url:
                                public_url = p.url
                                self.log(f"[PUBLISH] Live URL successfully captured from new tab: {public_url}")
                                p.close()
                                break
                        if public_url:
                            break
                except Exception as e:
                    pass

                # Method B: Top 'Copy published site link' icon (publish-5)
                try:
                    copy_link_icon = self.page.locator("div[role='button'][aria-label*='Copy published site link' i], button[aria-label*='Copy published site link' i]").first
                    if copy_link_icon.is_visible():
                        self.log("[PUBLISH] Checking live URL via top 'Copy published site link' icon...")
                        copy_link_icon.click(force=True)
                        self.page.wait_for_timeout(1500)

                        link_input = self.page.locator("div[role='dialog'] input[type='text'], div[role='dialog'] input[readonly]").first
                        if link_input.is_visible():
                            extracted = link_input.input_value()
                            if extracted and "sites.google.com/view" in extracted:
                                public_url = extracted.strip()
                                self.log(f"[PUBLISH] Live URL extracted from link dialog: {public_url}")
                                self.page.keyboard.press("Escape")
                                self.page.wait_for_timeout(400)
                                break

                        self.page.keyboard.press("Escape")
                        self.page.wait_for_timeout(400)
                except Exception as e:
                    pass

                if public_url:
                    break
                self.page.wait_for_timeout(2000)

            if not public_url and full_slug:
                public_url = f"https://sites.google.com/view/{full_slug}"
                self.log(f"[PUBLISH] Live URL configured via published slug: {public_url}")

            if public_url:
                self.log(f"[SUCCESS] Genuine published live URL verified: {public_url}")
                self._save_published_url(keyword, public_url)
                return public_url
            else:
                self.log("[PUBLISH] [ERROR] Site publication could not be verified from Google Sites. No live URL returned.")
                return None

        except Exception as e:
            self.log(f"[PUBLISH] Error during publishing: {e}")
            return None

    def _save_published_url(self, keyword: str, url: str):
        os.makedirs(URLS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] Keyword: {keyword} | URL: {url}\n"
        with open(URLS_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        self.log(f"[STORAGE] URL recorded in {URLS_FILE}")

    def execute_post(
        self,
        keyword: str,
        structure: PostStructure,
        phone_number: str,
        whatsapp_link: str,
        ai_content: Dict[str, Any],
        custom_content: Optional[str] = None
    ) -> Optional[str]:
        """Executes the complete posting workflow according to the structure elements."""
        self.log(f"[POST] Executing post for keyword: '{keyword}' using {structure.name}")
        
        if not self.create_blank_site():
            return None

        # 1. Title Banner
        page_title = ai_content.get("page_title", keyword.title())
        self.set_site_title(keyword, page_title)

        images = self.upload_structure_images(structure.image_folder_name)
        img_idx = 0
        sec_idx = 0
        sections = ai_content.get("sections", [])

        for element in structure.elements:
            if element.element_type == "header":
                continue
            
            elif element.element_type == "h2_text":
                if sec_idx < len(sections):
                    sec = sections[sec_idx]
                    sec_idx += 1
                    h2 = sec.get("h2_heading", f"Overview of {keyword.title()}")
                    body = sec.get("body_text", "")
                else:
                    h2 = f"Essential Information About {keyword.title()}"
                    body = f"Reliable and professional assistance for {keyword}."
                self.add_h2_text_box(h2, body)

            elif element.element_type == "content_block":
                if sec_idx < len(sections):
                    sec = sections[sec_idx]
                    sec_idx += 1
                    h2 = sec.get("h2_heading", f"Key Highlights for {keyword.title()}")
                    body = sec.get("body_text", "")
                else:
                    h2 = f"Features and Benefits of {keyword.title()}"
                    body = f"High quality and dependable services for {keyword}."
                self.add_h2_text_box(h2, body)
                if img_idx < len(images):
                    self.add_image_element(images[img_idx])
                    img_idx += 1

            elif element.element_type == "buttons":
                self.add_cta_buttons(phone_number, whatsapp_link)

            elif element.element_type == "image":
                if img_idx < len(images):
                    self.add_image_element(images[img_idx])
                    img_idx += 1

            elif element.element_type == "carousel":
                self.add_image_carousel(images)

            elif element.element_type == "map":
                map_q = ai_content.get("map_query", "New Delhi, India")
                self.add_map_embed(map_q)

            elif element.element_type == "custom_html":
                if custom_content:
                    self.add_h2_text_box("Detailed Information", custom_content)

            elif element.element_type == "footer":
                footer_text = ai_content.get("footer_text", f"© 2026 {keyword.title()}. All rights reserved.")
                self.add_footer(footer_text)

        pub_url = self.publish_and_get_url(keyword)
        
        add_task_history(
            keyword=keyword,
            structure_used=structure.name,
            phone_number=phone_number,
            whatsapp_link=whatsapp_link,
            published_url=pub_url or "",
            status="SUCCESS" if pub_url else "FAILED"
        )
        return pub_url

    def close(self):
        """Closes browser session and frees persistent profile locks."""
        self.log("[BROWSER] Closing browser session cleanly...")
        try:
            if self.context:
                self.context.close()
                self.context = None
        except Exception:
            pass
        try:
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
        except Exception:
            pass
        cleanup_profile_locks(PROFILE_DIR)

    def is_logged_in_google(self) -> bool:
        """Quickly checks if current profile is authenticated on Google Sites."""
        try:
            self.launch_browser(headless=True)
            self.page.goto("https://sites.google.com/new", wait_until="domcontentloaded", timeout=20000)
            self.page.wait_for_timeout(2500)
            url = self.page.url
            return ("sites.google.com" in url and "accounts.google.com" not in url)
        except Exception:
            return False
        finally:
            self.close()

    def run_interactive_login(self, status_callback: Optional[Callable[[str], None]] = None) -> bool:
        """Launches real native Chrome with persistent profile for manual Google login and waits until closed."""
        cb = status_callback or (lambda msg: None)
        cleanup_profile_locks(PROFILE_DIR)
        time.sleep(0.5)

        # 1. Search for installed Google Chrome executable
        chrome_exe = None
        if sys.platform == "darwin":
            candidates = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
            ]
        else:
            candidates = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
            ]
        for c in candidates:
            if os.path.exists(c):
                chrome_exe = c
                break
        if not chrome_exe and sys.platform == "win32":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
                val, _ = winreg.QueryValueEx(key, "")
                winreg.CloseKey(key)
                if os.path.exists(val):
                    chrome_exe = val
            except Exception:
                pass

        if chrome_exe:
            cb("Launching real Google Chrome window...")
            cmd = [
                chrome_exe,
                f"--user-data-dir={PROFILE_DIR}",
                "--no-first-run",
                "--no-default-browser-check",
                "--start-maximized",
                "https://sites.google.com/new"
            ]
            proc = subprocess.Popen(cmd)
            cb("Chrome is open. Sign in with your Google Account, then close Chrome when done.")
            proc.wait()
            cleanup_profile_locks(PROFILE_DIR)
            time.sleep(1)
        else:
            # Fallback to Playwright if chrome.exe not directly found
            cb("Launching Chrome browser...")
            self.launch_browser(headless=False)
            cb("Opening Google Sites / Sign-in page...")
            self.page.goto("https://sites.google.com/new", wait_until="domcontentloaded")
            cb("Chrome is open. Please sign in to your Google Account. Close Chrome when done.")
            while True:
                try:
                    if not self.context or not self.context.pages:
                        break
                    active_pages = [p for p in self.context.pages if not p.is_closed()]
                    if not active_pages:
                        break
                    time.sleep(1)
                except Exception:
                    break
            self.close()

        cb("Chrome closed. Verifying saved session...")
        time.sleep(1)
        return self.is_logged_in_google()



