"""
Admin License Key Generator & Supabase Manager Suite.
Generates HWID-locked license keys and automatically syncs with Supabase database.
"""

import sys
import os
import requests
from datetime import datetime, timedelta, timezone

# Ensure project root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QClipboard

from core.security.crypto_util import generate_license_key
from core.security.supabase_client import (
    insert_license_record, SUPABASE_URL, HEADERS
)

class KeygenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Sites Poster - Admin License Keygen & Manager")
        self.setFixedSize(860, 680)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1a1b26;
                color: #c0caf5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                border: 1px solid #414868;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                color: #7aa2f7;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
            }
            QLabel {
                color: #a9b1d6;
                font-size: 13px;
            }
            QLineEdit, QComboBox {
                background-color: #24283b;
                border: 1px solid #414868;
                border-radius: 6px;
                padding: 8px 12px;
                color: #c0caf5;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #7aa2f7;
            }
            QPushButton {
                background-color: #7aa2f7;
                color: #15161e;
                font-weight: bold;
                border-radius: 6px;
                padding: 9px 18px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
            }
            QPushButton#copyBtn {
                background-color: #9ece6a;
                color: #15161e;
            }
            QPushButton#copyBtn:hover {
                background-color: #b9f27c;
            }
            QPushButton#revokeBtn {
                background-color: #f7768e;
                color: #15161e;
                padding: 4px 10px;
                font-size: 11px;
            }
            QPushButton#revokeBtn:hover {
                background-color: #ff9eaf;
            }
            QTableWidget {
                background-color: #16161e;
                border: 1px solid #414868;
                border-radius: 6px;
                gridline-color: #292e42;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #24283b;
                color: #7aa2f7;
                font-weight: bold;
                border: 1px solid #414868;
                padding: 6px;
            }
        """)

        self._init_ui()
        self._refresh_licenses_table()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # Title Header
        header_row = QHBoxLayout()
        title = QLabel("🔑 Advanced License Keygen & Supabase Manager")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #7aa2f7;")
        header_row.addWidget(title)
        header_row.addStretch()

        refresh_btn = QPushButton("↻ Refresh Supabase Table")
        refresh_btn.clicked.connect(self._refresh_licenses_table)
        header_row.addWidget(refresh_btn)
        main_layout.addLayout(header_row)

        # Section 1: Generator Box
        gen_box = QGroupBox("Generate HWID-Locked License Key")
        gen_layout = QVBoxLayout(gen_box)
        gen_layout.setSpacing(12)

        # Row 1: HWID Input
        hwid_row = QHBoxLayout()
        hwid_lbl = QLabel("Client Hardware ID (HWID):")
        hwid_lbl.setFixedWidth(180)
        hwid_row.addWidget(hwid_lbl)

        self.hwid_input = QLineEdit()
        self.hwid_input.setPlaceholderText("Paste user's HWID (e.g. HWID-C1DE-CC9B-2436-7137)")
        hwid_row.addWidget(self.hwid_input)
        gen_layout.addLayout(hwid_row)

        # Row 2: Client Name & Expiry
        meta_row = QHBoxLayout()
        name_lbl = QLabel("Client Name / Note:")
        name_lbl.setFixedWidth(180)
        meta_row.addWidget(name_lbl)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Client Name (e.g. Rahul Sharma)")
        meta_row.addWidget(self.name_input)

        exp_lbl = QLabel("Validity:")
        meta_row.addWidget(exp_lbl)

        self.validity_cb = QComboBox()
        self.validity_cb.addItems(["Lifetime (Never Expires)", "30 Days", "90 Days", "180 Days", "1 Year"])
        meta_row.addWidget(self.validity_cb)
        gen_layout.addLayout(meta_row)

        # Row 3: Action Button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.gen_btn = QPushButton("⚡ Generate Key & Save to Supabase")
        self.gen_btn.setFixedWidth(280)
        self.gen_btn.clicked.connect(self._generate_and_save)
        btn_row.addWidget(self.gen_btn)
        btn_row.addStretch()
        gen_layout.addLayout(btn_row)

        # Row 4: Generated Key Display
        res_row = QHBoxLayout()
        res_lbl = QLabel("Generated License Key:")
        res_lbl.setFixedWidth(180)
        res_row.addWidget(res_lbl)

        self.key_display = QLineEdit()
        self.key_display.setReadOnly(True)
        self.key_display.setStyleSheet("font-family: 'Consolas', monospace; font-size: 15px; font-weight: bold; color: #9ece6a; background-color: #1f2335;")
        self.key_display.setPlaceholderText("Key will appear here after generation...")
        res_row.addWidget(self.key_display)

        self.copy_btn = QPushButton("Copy Key")
        self.copy_btn.setObjectName("copyBtn")
        self.copy_btn.clicked.connect(self._copy_key)
        res_row.addWidget(self.copy_btn)
        gen_layout.addLayout(res_row)

        main_layout.addWidget(gen_box)

        # Section 2: Supabase Licenses Table
        table_box = QGroupBox("Live Supabase Licenses Records")
        table_layout = QVBoxLayout(table_box)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Client Name", "License Key", "Hardware ID", "Status", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table_layout.addWidget(self.table)

        main_layout.addWidget(table_box)

    def _generate_and_save(self):
        hwid = self.hwid_input.text().strip().upper()
        if not hwid:
            QMessageBox.warning(self, "Missing HWID", "Please enter the client's Hardware ID (HWID).")
            return

        if not hwid.startswith("HWID-"):
            QMessageBox.warning(self, "Invalid HWID", "Hardware ID should start with 'HWID-'. Example: HWID-C1DE-CC9B-2436-7137")
            return

        client_name = self.name_input.text().strip() or "Client"
        validity = self.validity_cb.currentText()

        expires_at = None
        if "30 Days" in validity:
            expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        elif "90 Days" in validity:
            expires_at = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
        elif "180 Days" in validity:
            expires_at = (datetime.now(timezone.utc) + timedelta(days=180)).isoformat()
        elif "1 Year" in validity:
            expires_at = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()

        # Generate HWID-bound key
        key = generate_license_key(hwid, client_name)

        # Save to Supabase
        self.gen_btn.setEnabled(False)
        self.gen_btn.setText("Syncing with Supabase...")
        QApplication.processEvents()

        success, msg = insert_license_record(key, hwid, client_name=client_name, expires_at=expires_at)
        self.gen_btn.setEnabled(True)
        self.gen_btn.setText("⚡ Generate Key & Save to Supabase")

        if success:
            self.key_display.setText(key)
            QMessageBox.information(self, "Success", f"License generated and saved to Supabase!\n\nKey: {key}\nHWID: {hwid}\nClient: {client_name}")
            self._refresh_licenses_table()
        else:
            QMessageBox.critical(self, "Supabase Error", f"Could not save to Supabase:\n\n{msg}")

    def _copy_key(self):
        key = self.key_display.text().strip()
        if key:
            clipboard = QApplication.clipboard()
            clipboard.setText(key)
            self.copy_btn.setText("✓ Copied!")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("Copy Key"))

    def _refresh_licenses_table(self):
        url = f"{SUPABASE_URL}/rest/v1/licenses?select=*&order=id.desc"
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                rows = r.json()
                self.table.setRowCount(len(rows))
                for i, row in enumerate(rows):
                    rec_id = str(row.get("id", ""))
                    name = str(row.get("client_name", ""))
                    key = str(row.get("license_key", ""))
                    hwid = str(row.get("hardware_id", ""))
                    status = str(row.get("status", ""))
                    tamper = row.get("tamper_detected", False)

                    self.table.setItem(i, 0, QTableWidgetItem(rec_id))
                    self.table.setItem(i, 1, QTableWidgetItem(name))
                    self.table.setItem(i, 2, QTableWidgetItem(key))
                    self.table.setItem(i, 3, QTableWidgetItem(hwid))

                    status_item = QTableWidgetItem(status)
                    if status == "ACTIVE" and not tamper:
                        status_item.setForeground(Qt.green)
                    else:
                        status_item.setForeground(Qt.red)
                    self.table.setItem(i, 4, status_item)

                    # Action Button (Revoke)
                    revoke_btn = QPushButton("Revoke" if status == "ACTIVE" else "Delete")
                    revoke_btn.setObjectName("revokeBtn")
                    revoke_btn.clicked.connect(lambda ch, k=key, st=status: self._toggle_revoke(k, st))
                    self.table.setCellWidget(i, 5, revoke_btn)
        except Exception as e:
            pass

    def _toggle_revoke(self, license_key: str, current_status: str):
        if current_status == "ACTIVE":
            confirm = QMessageBox.question(
                self, "Revoke License",
                f"Are you sure you want to REVOKE license '{license_key}'?\nThe client software will instantly lock up and self-corrupt on next run!",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                url = f"{SUPABASE_URL}/rest/v1/licenses?license_key=eq.{license_key}"
                requests.patch(url, headers=HEADERS, json={"status": "REVOKED", "tamper_detected": True})
                self._refresh_licenses_table()
        else:
            confirm = QMessageBox.question(
                self, "Delete Record",
                f"Permanently delete license '{license_key}' from Supabase?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                url = f"{SUPABASE_URL}/rest/v1/licenses?license_key=eq.{license_key}"
                requests.delete(url, headers=HEADERS)
                self._refresh_licenses_table()

def main():
    app = QApplication(sys.argv)
    window = KeygenWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
