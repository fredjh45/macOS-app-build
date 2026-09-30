"""
Background Worker Thread (QThread) for executing single, bulk, and custom posting tasks.
Dispatches directly to isolated structure modules (structure_1, structure_2, etc.).
"""

import time
import logging
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QThread, Signal

from core.structures import get_structure_module, get_structure_module_by_index
from core.sites_engine import GoogleSitesAutomator

logger = logging.getLogger(__name__)

class PostingWorker(QThread):
    log_signal = Signal(str)
    status_signal = Signal(str)
    progress_signal = Signal(int, int)  # current, total
    url_published_signal = Signal(str, str)  # keyword, url
    finished_signal = Signal(bool, str)  # success, message

    def __init__(
        self,
        mode: str,  # 'single', 'bulk', 'custom'
        keywords: List[str],
        structure_id: str,
        phone_number: str = "",
        whatsapp_link: str = "",
        is_repeater: bool = False,
        custom_content: str = "",
        theme_name: str = "Simple",
        theme_color_hex: Optional[str] = None,
        enable_announcement: bool = False,
        announcement_message: Optional[str] = None,
        banner_color: Optional[str] = "#FF0000",
        headless: bool = False,
        parent=None
    ):
        super().__init__(parent)
        self.mode = mode
        self.keywords = [k.strip() for k in keywords if k.strip()]
        self.structure_id = structure_id
        self.phone_number = phone_number
        self.whatsapp_link = whatsapp_link
        self.is_repeater = is_repeater
        self.custom_content = custom_content
        self.theme_name = theme_name
        self.theme_color_hex = theme_color_hex
        self.enable_announcement = enable_announcement
        self.announcement_message = announcement_message
        self.banner_color = banner_color or "#FF0000"
        self.headless = headless
        self._is_running = True
        self.automator: Optional[GoogleSitesAutomator] = None

    def stop(self):
        """Requests graceful cancellation."""
        self._is_running = False
        self.log_signal.emit("[HALT] Stop requested. Halting tasks...")

    def run(self):
        total = len(self.keywords)
        if total == 0 and self.mode != "custom":
            self.finished_signal.emit(False, "No keywords provided.")
            return

        if self.mode == "custom" and not self.keywords:
            self.keywords = ["Custom Publication"]
            total = 1

        self.log_signal.emit(f"[TASK START] Starting posting workflow in {self.mode.upper()} mode ({total} items)...")
        self.log_signal.emit(f"[BROWSER CONFIG] Execution Mode: {'BACKGROUND (Silent)' if self.headless else 'VISIBLE (Desktop Window)'}")
        self.log_signal.emit(f"[THEME CONFIG] Selected Theme: '{self.theme_name}' | Custom Color: {self.theme_color_hex or 'Default'}")
        if self.enable_announcement:
            self.log_signal.emit(f"[BANNER CONFIG] Announcement Banner: ENABLED | Color: {self.banner_color}")
        if self.is_repeater:
            self.log_signal.emit("[REPEATER] Repeater mode active: Rotating Structure 1 -> 2 -> 3 -> 4 -> 1...")

        try:
            self.automator = GoogleSitesAutomator(log_callback=self.log_signal.emit)
            self.automator.launch_browser(headless=self.headless)

            if not self.automator.check_and_login_google():
                self.finished_signal.emit(False, "Google authentication could not be completed.")
                return

            completed_count = 0

            for idx, keyword in enumerate(self.keywords):
                if not self._is_running:
                    self.log_signal.emit("[HALT] Task interrupted by user.")
                    break

                self.progress_signal.emit(idx + 1, total)
                self.status_signal.emit(f"Processing ({idx+1}/{total}): {keyword}")

                # Determine Structure Module
                if self.mode == "custom":
                    struct_mod = get_structure_module("str-custom")
                elif self.is_repeater:
                    struct_index = (idx % 4) + 1
                    struct_mod = get_structure_module_by_index(struct_index)
                    self.log_signal.emit(f"[REPEATER] Cycle selected: {struct_mod.STRUCTURE_NAME} for '{keyword}'")
                else:
                    struct_mod = get_structure_module(self.structure_id)

                # Execute through the isolated structure module
                if self.mode == "custom":
                    pub_url = struct_mod.execute_structure_custom(
                        self.automator,
                        title=keyword,
                        phone_number=self.phone_number,
                        whatsapp_link=self.whatsapp_link,
                        custom_content=self.custom_content,
                        theme_name=self.theme_name,
                        theme_color_hex=self.theme_color_hex,
                        enable_announcement=self.enable_announcement,
                        announcement_message=self.announcement_message,
                        banner_color=self.banner_color
                    )
                elif struct_mod.STRUCTURE_ID == "str-1":
                    pub_url = struct_mod.execute_structure_1(
                        self.automator,
                        keyword=keyword,
                        phone_number=self.phone_number,
                        whatsapp_link=self.whatsapp_link,
                        ai_content=None,  # let structure_1 generate its exact schema
                        related_keywords=self.keywords,
                        theme_name=self.theme_name,
                        theme_color_hex=self.theme_color_hex,
                        enable_announcement=self.enable_announcement,
                        announcement_message=self.announcement_message,
                        banner_color=self.banner_color
                    )
                else:
                    # Generic executor for structure 2, 3, 4
                    struct_num = struct_mod.STRUCTURE_ID.split('-')[-1]
                    execute_fn = (
                        getattr(struct_mod, f"execute_structure_{struct_num}", None)
                        or getattr(struct_mod, f"execute_{struct_mod.STRUCTURE_ID.replace('-', '_')}", None)
                        or getattr(struct_mod, f"execute_str_{struct_num}", None)
                        or getattr(struct_mod, "execute_structure_2", None)
                    )
                    if not execute_fn:
                        raise AttributeError(f"Could not find execute function for {struct_mod.STRUCTURE_ID} in {struct_mod.__name__}")
                    pub_url = execute_fn(
                        self.automator,
                        keyword=keyword,
                        phone_number=self.phone_number,
                        whatsapp_link=self.whatsapp_link,
                        ai_content=None,
                        related_keywords=self.keywords,
                        theme_name=self.theme_name,
                        theme_color_hex=self.theme_color_hex,
                        enable_announcement=self.enable_announcement,
                        announcement_message=self.announcement_message,
                        banner_color=self.banner_color
                    )

                if pub_url:
                    completed_count += 1
                    self.url_published_signal.emit(keyword, pub_url)

                if idx < total - 1 and self._is_running:
                    self.log_signal.emit("[COOLDOWN] Waiting 8 seconds before next site creation...")
                    for _ in range(8):
                        if not self._is_running:
                            break
                        time.sleep(1)

            summary = f"Task completed: Successfully published {completed_count}/{total} sites."
            self.log_signal.emit(f"[COMPLETE] {summary}")
            self.finished_signal.emit(True, summary)

        except Exception as e:
            logger.exception(f"Exception in Worker: {e}")
            self.log_signal.emit(f"[ERROR] Exception during execution: {e}")
            self.finished_signal.emit(False, str(e))
        finally:
            if self.automator:
                self.automator.close()
