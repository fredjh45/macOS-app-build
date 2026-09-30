"""
Activation Dialog for Google Sites Automated Poster.
Presented when no valid license is detected. Shows machine HWID with copy button.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QApplication
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QIcon, QClipboard

from core.security.license_guard import LicenseGuard

class ActivationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Software Activation - Node Lock Protection")
        self.setFixedSize(560, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1b26;
                color: #c0caf5;
            }
            QLabel {
                color: #c0caf5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                background-color: #24283b;
                border: 1px solid #414868;
                border-radius: 6px;
                padding: 10px;
                color: #7aa2f7;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 1px solid #7aa2f7;
            }
            QPushButton {
                background-color: #7aa2f7;
                color: #15161e;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
            }
            QPushButton#copyBtn {
                background-color: #3b4261;
                color: #c0caf5;
            }
            QPushButton#copyBtn:hover {
                background-color: #414868;
            }
            QPushButton#exitBtn {
                background-color: #f7768e;
                color: #15161e;
            }
            QPushButton#exitBtn:hover {
                background-color: #ff9eaf;
            }
        """)

        self.hwid = LicenseGuard.get_hwid()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header Title
        title_label = QLabel("License Key Required")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #7aa2f7;")
        layout.addWidget(title_label)

        desc_label = QLabel(
            "This software is protected with single-machine node-locking. "
            "Please copy your unique <b>Hardware ID</b> below and share it with the administrator to generate your License Key."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #9aa5ce; font-size: 12px; line-height: 1.4;")
        layout.addWidget(desc_label)

        # HWID Section
        hwid_label = QLabel("Your Machine Hardware ID:")
        hwid_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #bb9af7;")
        layout.addWidget(hwid_label)

        hwid_row = QHBoxLayout()
        self.hwid_input = QLineEdit(self.hwid)
        self.hwid_input.setReadOnly(True)
        self.hwid_input.setAlignment(Qt.AlignCenter)
        hwid_row.addWidget(self.hwid_input)

        copy_btn = QPushButton("Copy HWID")
        copy_btn.setObjectName("copyBtn")
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(self._copy_hwid)
        hwid_row.addWidget(copy_btn)
        layout.addLayout(hwid_row)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #292e42;")
        layout.addWidget(line)

        # License Key Input Section
        key_label = QLabel("Enter License Key:")
        key_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #7dcfff;")
        layout.addWidget(key_label)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("GSITE-XXXX-XXXX-XXXX-XXXX")
        self.key_input.setAlignment(Qt.AlignCenter)
        self.key_input.textChanged.connect(self._format_key_input)
        layout.addWidget(self.key_input)

        # Status Label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Bottom Buttons
        btn_row = QHBoxLayout()
        exit_btn = QPushButton("Exit")
        exit_btn.setObjectName("exitBtn")
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.clicked.connect(self.reject)
        btn_row.addWidget(exit_btn)

        self.activate_btn = QPushButton("Activate License")
        self.activate_btn.setCursor(Qt.PointingHandCursor)
        self.activate_btn.clicked.connect(self._activate)
        btn_row.addWidget(self.activate_btn)
        layout.addLayout(btn_row)

    def _copy_hwid(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.hwid)
        self.status_label.setStyleSheet("color: #9ece6a;")
        self.status_label.setText("✓ Hardware ID copied to clipboard!")
        QTimer.singleShot(2500, lambda: self.status_label.setText(""))

    def _format_key_input(self, text: str):
        upper_text = text.upper()
        if upper_text != text:
            cursor_pos = self.key_input.cursorPosition()
            self.key_input.setText(upper_text)
            self.key_input.setCursorPosition(cursor_pos)

    def _activate(self):
        raw_key = self.key_input.text().strip().upper()
        if not raw_key:
            self.status_label.setStyleSheet("color: #f7768e;")
            self.status_label.setText("Please enter your License Key.")
            return

        self.activate_btn.setEnabled(False)
        self.activate_btn.setText("Validating...")
        self.key_input.setEnabled(False)
        self.status_label.setStyleSheet("color: #7aa2f7;")
        self.status_label.setText("Validating license with server...")

        self.worker = ActivationWorker(raw_key, self)
        self.worker.finished.connect(self._on_activation_finished)
        self.worker.start()

    def _on_activation_finished(self, success: bool, msg: str):
        self.key_input.setEnabled(True)
        self.activate_btn.setText("Activate License")
        if success:
            self.status_label.setStyleSheet("color: #9ece6a; font-size: 13px;")
            self.status_label.setText("✓ " + msg)
            QTimer.singleShot(1000, self.accept)
        else:
            self.status_label.setStyleSheet("color: #f7768e;")
            self.status_label.setText("✗ " + msg)
            self.activate_btn.setEnabled(True)


class ActivationWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, key: str, parent=None):
        super().__init__(parent)
        self.key = key

    def run(self):
        success, msg = LicenseGuard.activate(self.key)
        self.finished.emit(success, msg)

