"""
Settings Tab: Manages Google account credentials and DeepSeek / Grok API keys.
Emojis removed, replaced with clean styling and standard Qt icons.
"""

import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QComboBox, QMessageBox,
    QApplication, QStyle, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal

from database.db import get_setting, save_settings

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.load_settings()

    def _init_ui(self):
        style = QApplication.style()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll Area for clean rendering when window is resized or maximized
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(24, 20, 24, 20)

        # 2-Column Responsive Layout
        cols_layout = QHBoxLayout()
        cols_layout.setSpacing(20)

        # ----------------- Column 1: Google Account & Session -----------------
        google_group = QGroupBox("Google Account Credentials and Browser Session")
        g_layout = QVBoxLayout(google_group)
        g_layout.setSpacing(10)
        g_layout.setContentsMargins(18, 16, 18, 16)

        # Email
        g_layout.addWidget(QLabel("Gmail Address:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your-email@gmail.com")
        g_layout.addWidget(self.email_input)

        # Password
        g_layout.addWidget(QLabel("Google Account Password:"))
        self.pass_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your account password")
        
        self.show_pass_btn = QPushButton("Show")
        self.show_pass_btn.setFixedWidth(75)
        self.show_pass_btn.clicked.connect(self._toggle_pass_visibility)
        
        self.pass_layout.addWidget(self.password_input)
        self.pass_layout.addWidget(self.show_pass_btn)
        g_layout.addLayout(self.pass_layout)

        # Recovery Email / Phone
        g_layout.addWidget(QLabel("Recovery Email / Phone (Optional for 2FA verification):"))
        self.recovery_input = QLineEdit()
        self.recovery_input.setPlaceholderText("recovery-email@gmail.com")
        g_layout.addWidget(self.recovery_input)

        # Manual Login & Session Persistence
        session_header = QLabel("Google Account Session (Chrome Profile):")
        session_header.setStyleSheet("font-weight: bold; margin-top: 6px;")
        g_layout.addWidget(session_header)

        session_help = QLabel(
            "Recommended: Click 'Open Chrome to Login Google Account' once. "
            "A normal Chrome browser will open where you can sign in with your Google account. "
            "Once logged in, close Chrome. Your session will be saved permanently, bypassing 2FA."
        )
        session_help.setWordWrap(True)
        session_help.setStyleSheet("color: #a9b1d6; font-size: 12px; margin-bottom: 4px;")
        g_layout.addWidget(session_help)

        session_btn_row1 = QHBoxLayout()
        session_btn_row1.setSpacing(10)

        self.open_chrome_btn = QPushButton("Open Chrome to Login Google Account")
        self.open_chrome_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.open_chrome_btn.setStyleSheet(
            "background-color: #2ac3de; color: #15161e; font-weight: bold; font-size: 13px; padding: 10px 18px; border-radius: 6px;"
        )
        self.open_chrome_btn.clicked.connect(self.open_chrome_login)
        session_btn_row1.addWidget(self.open_chrome_btn)

        self.check_session_btn = QPushButton("Check Login Status")
        self.check_session_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self.check_session_btn.setStyleSheet(
            "background-color: #3b4261; color: #c0caf5; font-weight: bold; font-size: 13px; padding: 10px 16px; border-radius: 6px;"
        )
        self.check_session_btn.clicked.connect(self.check_google_session)
        session_btn_row1.addWidget(self.check_session_btn)

        g_layout.addLayout(session_btn_row1)

        self.clear_cache_btn = QPushButton("Clear Tool Cache and Reset")
        self.clear_cache_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton))
        self.clear_cache_btn.setStyleSheet(
            "background-color: #f7768e; color: #15161e; font-weight: bold; font-size: 13px; padding: 9px 16px; border-radius: 6px;"
        )
        self.clear_cache_btn.clicked.connect(self.clear_tool_cache)
        g_layout.addWidget(self.clear_cache_btn)

        self.session_status_label = QLabel("Session Status: Ready (Click 'Check Login Status' to verify)")
        self.session_status_label.setStyleSheet("color: #7aa2f7; font-size: 12px; font-weight: bold; margin-top: 4px;")
        g_layout.addWidget(self.session_status_label)
        g_layout.addStretch()

        cols_layout.addWidget(google_group, 1)

        # ----------------- Column 2: AI API Settings -----------------
        ai_group = QGroupBox("AI Engine and API Configuration (Content Generation)")
        ai_layout = QVBoxLayout(ai_group)
        ai_layout.setSpacing(10)
        ai_layout.setContentsMargins(18, 16, 18, 16)

        # Provider Selection
        ai_layout.addWidget(QLabel("Active AI Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["DeepSeek", "Grok (xAI)"])
        ai_layout.addWidget(self.provider_combo)

        # DeepSeek Key
        ai_layout.addWidget(QLabel("DeepSeek API Key:"))
        self.deepseek_key_input = QLineEdit()
        self.deepseek_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.deepseek_key_input.setPlaceholderText("sk-...")
        ai_layout.addWidget(self.deepseek_key_input)

        # Grok Key
        ai_layout.addWidget(QLabel("Grok (xAI) API Key:"))
        self.grok_key_input = QLineEdit()
        self.grok_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.grok_key_input.setPlaceholderText("xai-...")
        ai_layout.addWidget(self.grok_key_input)

        ai_help = QLabel(
            "Configure your preferred AI provider to automatically generate unique, SEO-optimized "
            "headings and articles for each published Google Site."
        )
        ai_help.setWordWrap(True)
        ai_help.setStyleSheet("color: #a9b1d6; font-size: 12px; margin-top: 6px;")
        ai_layout.addWidget(ai_help)

        self.test_ai_btn = QPushButton("Test AI Connection")
        self.test_ai_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_CommandLink))
        self.test_ai_btn.setStyleSheet(
            "background-color: #3b4261; color: #c0caf5; font-weight: bold; font-size: 13px; padding: 10px 18px; border-radius: 6px;"
        )
        self.test_ai_btn.clicked.connect(self.test_ai_connection)
        ai_layout.addWidget(self.test_ai_btn)

        ai_layout.addStretch()

        cols_layout.addWidget(ai_group, 1)

        content_layout.addLayout(cols_layout)

        # ----------------- Bottom Action Bar -----------------
        act_layout = QHBoxLayout()
        act_layout.addStretch()

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.save_btn.setStyleSheet(
            "background-color: #9ece6a; color: #15161e; font-weight: bold; font-size: 14px; padding: 11px 34px; border-radius: 6px;"
        )
        self.save_btn.clicked.connect(self.save_settings)
        act_layout.addWidget(self.save_btn)

        content_layout.addLayout(act_layout)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _toggle_pass_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pass_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pass_btn.setText("Show")

    def load_settings(self):
        self.email_input.setText(get_setting("gmail_email", ""))
        self.password_input.setText(get_setting("gmail_password", ""))
        self.recovery_input.setText(get_setting("recovery_email", ""))
        
        active_provider = get_setting("active_ai_provider", "DeepSeek")
        idx = self.provider_combo.findText(active_provider, Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)

        self.deepseek_key_input.setText(get_setting("deepseek_api_key", ""))
        self.grok_key_input.setText(get_setting("grok_api_key", ""))

    def save_settings(self):
        settings_dict = {
            "gmail_email": self.email_input.text().strip(),
            "gmail_password": self.password_input.text().strip(),
            "recovery_email": self.recovery_input.text().strip(),
            "active_ai_provider": self.provider_combo.currentText(),
            "deepseek_api_key": self.deepseek_key_input.text().strip(),
            "grok_api_key": self.grok_key_input.text().strip()
        }
        save_settings(settings_dict)
        QMessageBox.information(self, "Success", "Settings have been successfully saved into SQLite database.")

    def test_ai_connection(self):
        provider = self.provider_combo.currentText()
        if "DeepSeek" in provider:
            key = self.deepseek_key_input.text().strip()
            url = "https://api.deepseek.com/chat/completions"
            model = "deepseek-chat"
        else:
            key = self.grok_key_input.text().strip()
            url = "https://api.x.ai/v1/chat/completions"
            model = "grok-4.3"

        if not key:
            QMessageBox.warning(self, "Missing Key", f"Please enter an API key for {provider} first.")
            return

        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 5
            }
            if "Grok" in provider or "grok" in provider.lower():
                payload["reasoning_effort"] = "none"

            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=payload,
                timeout=12
            )
            if r.status_code == 200:
                QMessageBox.information(self, "Success", f"{provider} API connection verified successfully.")
            else:
                QMessageBox.critical(self, "Connection Error", f"API returned status code {r.status_code}:\n{r.text[:200]}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reach {provider} API:\n{e}")

    def open_chrome_login(self):
        self.open_chrome_btn.setEnabled(False)
        self.check_session_btn.setEnabled(False)
        self.open_chrome_btn.setText("Chrome is Open... Log in & Close Chrome")
        self.session_status_label.setText("Chrome is running. Please sign into your Google account in Chrome...")
        self.session_status_label.setStyleSheet("color: #2ac3de; font-size: 12px; font-weight: bold;")

        self.login_worker = GoogleSessionLoginWorker(self)
        self.login_worker.status_updated.connect(self._on_login_status_update)
        self.login_worker.finished.connect(self._on_login_finished)
        self.login_worker.start()

    def _on_login_status_update(self, msg: str):
        self.session_status_label.setText(f"{msg}")

    def _on_login_finished(self, is_logged_in: bool, msg: str):
        self.open_chrome_btn.setEnabled(True)
        self.check_session_btn.setEnabled(True)
        self.open_chrome_btn.setText("Open Chrome to Login Google Account")

        if is_logged_in:
            self.session_status_label.setText("Google Session Saved Successfully (Logged In)!")
            self.session_status_label.setStyleSheet("color: #9ece6a; font-size: 12px; font-weight: bold;")
            QMessageBox.information(
                self,
                "Google Session Saved",
                "Google account is successfully logged in and session is saved!\n\n"
                "You can now create and post Google Sites smoothly without any 2FA or login interruptions."
            )
        else:
            self.session_status_label.setText("Chrome was closed. (Click 'Check Login Status' to verify)")
            self.session_status_label.setStyleSheet("color: #e0af68; font-size: 12px; font-weight: bold;")

    def check_google_session(self):
        self.check_session_btn.setEnabled(False)
        self.session_status_label.setText("Verifying Google Sites session...")
        self.session_status_label.setStyleSheet("color: #e0af68; font-size: 12px; font-weight: bold;")

        self.check_worker = GoogleCheckSessionWorker(self)
        self.check_worker.finished.connect(self._on_check_finished)
        self.check_worker.start()

    def _on_check_finished(self, is_logged_in: bool):
        self.check_session_btn.setEnabled(True)
        if is_logged_in:
            self.session_status_label.setText("Google Sites: Active Logged-in Session Detected!")
            self.session_status_label.setStyleSheet("color: #9ece6a; font-size: 12px; font-weight: bold;")
            QMessageBox.information(self, "Status: Active", "Your Google account is already logged in on Google Sites!")
        else:
            self.session_status_label.setText("Google Sites: Not Logged In. Please click 'Open Chrome to Login'.")
            self.session_status_label.setStyleSheet("color: #f7768e; font-size: 12px; font-weight: bold;")
            QMessageBox.warning(
                self,
                "Not Logged In",
                "No active Google Sites session found.\n\n"
                "Please click 'Open Chrome to Login Google Account', sign in once, and close Chrome."
            )

    def clear_tool_cache(self):
        confirm = QMessageBox.question(
            self,
            "Clear Tool Browser Cache & Session?",
            "Are you sure you want to clear the tool's internal stealth browser cache?\n\n"
            "• This will free up 500+ MB of temporary cache and cookies.\n"
            "• Your License Key activation will remain 100% SAFE and intact.\n"
            "• Old stuck Google sessions will be reset so you can bind a fresh Gmail account.\n\n"
            "Do you want to proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self.clear_cache_btn.setEnabled(False)
        self.session_status_label.setText("Clearing tool browser cache and resetting session...")
        self.session_status_label.setStyleSheet("color: #e0af68; font-size: 12px; font-weight: bold;")
        QApplication.processEvents()

        from core.sites_engine import clear_browser_cache_and_session
        ok, msg, freed_mb = clear_browser_cache_and_session()
        self.clear_cache_btn.setEnabled(True)

        if ok:
            self.session_status_label.setText(f"Cleared {freed_mb} MB cache! Session reset.")
            self.session_status_label.setStyleSheet("color: #9ece6a; font-size: 12px; font-weight: bold;")
            QMessageBox.information(
                self,
                "Tool Cache Cleared",
                f"Successfully freed {freed_mb} MB of temporary files!\n\n"
                "The tool's stealth browser is now clean, light, and loads instantly.\n"
                "You can now click 'Open Chrome to Login Google Account' to log in with a fresh Gmail."
            )
        else:
            self.session_status_label.setText("Error clearing cache.")
            self.session_status_label.setStyleSheet("color: #f7768e; font-size: 12px; font-weight: bold;")
            QMessageBox.critical(self, "Error", f"Failed to clear cache: {msg}")


class GoogleSessionLoginWorker(QThread):
    status_updated = Signal(str)
    finished = Signal(bool, str)

    def run(self):
        from core.sites_engine import GoogleSitesAutomator
        try:
            automator = GoogleSitesAutomator(log_callback=lambda msg: self.status_updated.emit(msg))
            is_logged_in = automator.run_interactive_login(status_callback=lambda msg: self.status_updated.emit(msg))
            if is_logged_in:
                self.finished.emit(True, "Google account is logged in and session is successfully saved!")
            else:
                self.finished.emit(False, "Chrome closed. Google account is not signed in yet.")
        except Exception as e:
            self.finished.emit(False, f"Error launching login session: {e}")


class GoogleCheckSessionWorker(QThread):
    finished = Signal(bool)

    def run(self):
        from core.sites_engine import GoogleSitesAutomator
        try:
            automator = GoogleSitesAutomator()
            is_ok = automator.is_logged_in_google()
            self.finished.emit(is_ok)
        except Exception:
            self.finished.emit(False)

