"""
Main Window for Google Sites Poster application.
Integrates Post Workstation and Settings Tabs with clean professional styling.
All emojis removed and replaced with standard Qt icons and clean typography.
"""

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QStatusBar, QLabel,
    QApplication, QStyle
)
from PySide6.QtCore import Qt

from ui.post_tab import PostTab
from ui.settings_tab import SettingsTab
from ui.styles import DARK_STYLESHEET
from database.db import get_setting

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Sites Automated Poster Suite")
        self.resize(1120, 840)
        self.setStyleSheet(DARK_STYLESHEET)

        self._init_ui()
        self._init_status_bar()

    def _init_ui(self):
        style = QApplication.style()
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Tab Widget
        self.tabs = QTabWidget(self)
        
        # 1. Post Tab
        self.post_tab = PostTab(self)
        self.tabs.addTab(
            self.post_tab,
            style.standardIcon(QStyle.StandardPixmap.SP_DesktopIcon),
            "Post Workstation"
        )

        # 2. Settings Tab
        self.settings_tab = SettingsTab(self)
        self.tabs.addTab(
            self.settings_tab,
            style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView),
            "Settings and API"
        )

        layout.addWidget(self.tabs)

    def _init_status_bar(self):
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.db_status_lbl = QLabel("Database: Connected")
        self.db_status_lbl.setStyleSheet("color: #9ece6a; margin-right: 15px; font-weight: 500;")
        
        provider = get_setting("active_ai_provider", "DeepSeek")
        self.ai_status_lbl = QLabel(f"Active AI: {provider}")
        self.ai_status_lbl.setStyleSheet("color: #7aa2f7; margin-right: 15px; font-weight: 500;")

        self.status_bar.addPermanentWidget(self.db_status_lbl)
        self.status_bar.addPermanentWidget(self.ai_status_lbl)
        self.status_bar.showMessage("Ready. Configure settings or launch posting task.", 5000)
