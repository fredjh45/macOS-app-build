"""
Post Tab: Workstation for Single Keyword, Bulk Posting with Repeater,
Native Rich Text Editor for Custom Content, Image Manager for 4 Structures,
and Execution Controls (Start / Stop Task).
All emojis removed and replaced with clean professional styling and Qt icons.
"""

import os
import shutil
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QRadioButton, QButtonGroup,
    QStackedWidget, QPlainTextEdit, QProgressBar, QTextEdit,
    QFileDialog, QComboBox, QMessageBox, QDialog, QSplitter,
    QApplication, QStyle, QColorDialog, QCheckBox
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from core.worker import PostingWorker
from core.structures import STRUCTURE_1, STRUCTURE_2, STRUCTURE_3, STRUCTURE_4
from ui.editor_view import RichTextEditorWidget
from database.db import get_setting, set_setting

from core.path_helper import get_base_dir, get_images_dir
BASE_DIR = get_base_dir()
IMAGES_DIR = get_images_dir()

class ImageUploadDialog(QDialog):
    """Dialog to upload an image and assign it to str-image1..4."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upload Image to Structure")
        self.setFixedWidth(440)
        self.selected_file_path = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Select Target Structure Folder:"))
        self.struct_combo = QComboBox()
        self.struct_combo.addItems([
            "str-image1 (Structure 1: Classic Service)",
            "str-image2 (Structure 2: Product Showcase)",
            "str-image3 (Structure 3: Lead Funnel)",
            "str-image4 (Structure 4: Authority Guide)"
        ])
        layout.addWidget(self.struct_combo)

        file_row = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #7aa2f7;")
        
        browse_btn = QPushButton("Browse Image...")
        browse_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        browse_btn.clicked.connect(self._browse_image)
        
        file_row.addWidget(self.file_label)
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        actions = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        upload_btn = QPushButton("Upload and Save")
        upload_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        upload_btn.setStyleSheet("background-color: #9ece6a; color: #15161e; font-weight: bold;")
        upload_btn.clicked.connect(self._save_image)
        actions.addWidget(cancel_btn)
        actions.addWidget(upload_btn)
        layout.addLayout(actions)

    def _browse_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self.selected_file_path = path
            self.file_label.setText(os.path.basename(path))

    def _save_image(self):
        if not self.selected_file_path or not os.path.exists(self.selected_file_path):
            QMessageBox.warning(self, "Warning", "Please select an image file first.")
            return

        folder_map = {
            0: "str-image1",
            1: "str-image2",
            2: "str-image3",
            3: "str-image4"
        }
        target_folder_name = folder_map.get(self.struct_combo.currentIndex(), "str-image1")
        target_dir = os.path.join(IMAGES_DIR, target_folder_name)
        os.makedirs(target_dir, exist_ok=True)

        dest_filename = os.path.basename(self.selected_file_path)
        dest_path = os.path.join(target_dir, dest_filename)
        shutil.copy2(self.selected_file_path, dest_path)

        QMessageBox.information(
            self, "Success",
            f"Image saved to '{target_folder_name}/{dest_filename}'."
        )
        self.accept()


class PostTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker: Optional[PostingWorker] = None
        self._init_ui()

    def _init_ui(self):
        style = QApplication.style()
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # 1. TOP RIBBON BAR
        ribbon_box = QGroupBox("Action Ribbon")
        ribbon_layout = QHBoxLayout(ribbon_box)
        ribbon_layout.setSpacing(10)

        # Mode Switch Buttons
        self.single_mode_btn = QPushButton("Single Keyword")
        self.single_mode_btn.setObjectName("ribbon_mode_btn")
        self.single_mode_btn.setCheckable(True)
        self.single_mode_btn.setChecked(True)
        self.single_mode_btn.clicked.connect(lambda: self._switch_mode(0))

        self.bulk_mode_btn = QPushButton("Bulk Keywords")
        self.bulk_mode_btn.setObjectName("ribbon_mode_btn")
        self.bulk_mode_btn.setCheckable(True)
        self.bulk_mode_btn.clicked.connect(lambda: self._switch_mode(1))

        self.custom_mode_btn = QPushButton("Custom Content (Rich Editor)")
        self.custom_mode_btn.setObjectName("ribbon_mode_btn")
        self.custom_mode_btn.setCheckable(True)
        self.custom_mode_btn.clicked.connect(lambda: self._switch_mode(2))

        # Upload Image Action
        self.upload_img_btn = QPushButton("Upload Image...")
        self.upload_img_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder))
        self.upload_img_btn.setStyleSheet("background-color: #bb9af7; color: #15161e; font-weight: bold;")
        self.upload_img_btn.clicked.connect(self._open_image_upload_dialog)

        # Theme Selector in Ribbon
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: #bb9af7; font-weight: bold; margin-left: 6px;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Simple",
            "Aristotle",
            "Diplomat",
            "Vision",
            "Level",
            "Impression"
        ])
        self.theme_combo.setToolTip("Select Google Sites Theme (Default: Simple)")

        # Announcement Banner Checkbox
        self.announcement_cb = QCheckBox("Announcement Banner")
        self.announcement_cb.setToolTip("Enable top sticky Announcement Banner with CTA and link")
        self.announcement_cb.setStyleSheet("color: #7aa2f7; font-weight: bold; margin-left: 6px;")

        # Action Execution Buttons
        self.start_task_btn = QPushButton("Start Task")
        self.start_task_btn.setObjectName("start_btn")
        self.start_task_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.start_task_btn.clicked.connect(self.start_task)

        self.stop_task_btn = QPushButton("Stop Task")
        self.stop_task_btn.setObjectName("stop_btn")
        self.stop_task_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_task_btn.setEnabled(False)
        self.stop_task_btn.clicked.connect(self.stop_task)

        ribbon_layout.addWidget(self.single_mode_btn)
        ribbon_layout.addWidget(self.bulk_mode_btn)
        ribbon_layout.addWidget(self.custom_mode_btn)
        ribbon_layout.addWidget(self.upload_img_btn)
        ribbon_layout.addWidget(theme_label)
        ribbon_layout.addWidget(self.theme_combo)
        ribbon_layout.addWidget(self.announcement_cb)
        ribbon_layout.addStretch()
        ribbon_layout.addWidget(self.start_task_btn)
        ribbon_layout.addWidget(self.stop_task_btn)

        main_layout.addWidget(ribbon_box)

        # 2. MIDDLE SPLITTER (Workspace & Real-time Logs)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Top half: Stacked View for modes
        self.stack = QStackedWidget()
        self.single_widget = self._create_single_keyword_view()
        self.bulk_widget = self._create_bulk_keywords_view()
        self.custom_widget = self._create_custom_content_view()

        self.stack.addWidget(self.single_widget)
        self.stack.addWidget(self.bulk_widget)
        self.stack.addWidget(self.custom_widget)
        splitter.addWidget(self.stack)

        # Bottom half: Logs & Progress Console
        bottom_console = self._create_console_view()
        splitter.addWidget(bottom_console)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        main_layout.addWidget(splitter)

    def _switch_mode(self, index: int):
        self.single_mode_btn.setChecked(index == 0)
        self.bulk_mode_btn.setChecked(index == 1)
        self.custom_mode_btn.setChecked(index == 2)
        self.stack.setCurrentIndex(index)

    def _create_single_keyword_view(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        # Left Column: Inputs
        left_box = QGroupBox("Single Keyword Inputs")
        left_layout = QVBoxLayout(left_box)
        left_layout.setSpacing(8)

        left_layout.addWidget(QLabel("Target Keyword (AI generates content based on this):"))
        self.single_kw_input = QLineEdit()
        self.single_kw_input.setPlaceholderText("e.g., Best Pest Control Service in Mumbai")
        left_layout.addWidget(self.single_kw_input)

        left_layout.addWidget(QLabel("Phone Number (Buttons Only):"))
        self.single_phone_input = QLineEdit()
        self.single_phone_input.setPlaceholderText("+91 9876543210")
        left_layout.addWidget(self.single_phone_input)

        left_layout.addWidget(QLabel("WhatsApp Link or Number (Buttons Only):"))
        self.single_wa_input = QLineEdit()
        self.single_wa_input.setPlaceholderText("https://wa.me/919876543210 or 9876543210")
        left_layout.addWidget(self.single_wa_input)

        left_layout.addStretch()
        layout.addWidget(left_box, 1)

        # Right Column: Vertical Structures Selector
        right_box = QGroupBox("Select Structure (Vertical)")
        right_layout = QVBoxLayout(right_box)
        right_layout.setSpacing(12)

        self.single_struct_group = QButtonGroup(self)
        self.s_rad1 = QRadioButton(STRUCTURE_1.name)
        self.s_rad2 = QRadioButton(STRUCTURE_2.name)
        self.s_rad3 = QRadioButton(STRUCTURE_3.name)
        self.s_rad4 = QRadioButton(STRUCTURE_4.name)

        self.s_rad1.setToolTip(STRUCTURE_1.description)
        self.s_rad2.setToolTip(STRUCTURE_2.description)
        self.s_rad3.setToolTip(STRUCTURE_3.description)
        self.s_rad4.setToolTip(STRUCTURE_4.description)

        self.s_rad1.setChecked(True)
        self.single_struct_group.addButton(self.s_rad1, 1)
        self.single_struct_group.addButton(self.s_rad2, 2)
        self.single_struct_group.addButton(self.s_rad3, 3)
        self.single_struct_group.addButton(self.s_rad4, 4)

        right_layout.addWidget(self.s_rad1)
        right_layout.addWidget(self.s_rad2)
        right_layout.addWidget(self.s_rad3)
        right_layout.addWidget(self.s_rad4)
        right_layout.addStretch()
        layout.addWidget(right_box, 1)

        return widget

    def _create_bulk_keywords_view(self) -> QWidget:
        style = QApplication.style()
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        # Left Column: Bulk Inputs
        left_box = QGroupBox("Bulk Keywords Input")
        left_layout = QVBoxLayout(left_box)
        left_layout.setSpacing(8)

        file_bar = QHBoxLayout()
        file_bar.addWidget(QLabel("Keywords (One per line):"))
        file_bar.addStretch()
        
        import_btn = QPushButton("Load from File...")
        import_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        import_btn.clicked.connect(self._load_keywords_from_file)
        file_bar.addWidget(import_btn)
        left_layout.addLayout(file_bar)

        self.bulk_kw_text = QPlainTextEdit()
        self.bulk_kw_text.setPlaceholderText("Keyword 1\nKeyword 2\nKeyword 3\nKeyword 4\nKeyword 5...")
        left_layout.addWidget(self.bulk_kw_text)

        contact_row = QHBoxLayout()
        c_left = QVBoxLayout()
        c_left.addWidget(QLabel("Phone Number (Buttons Only):"))
        self.bulk_phone_input = QLineEdit()
        self.bulk_phone_input.setPlaceholderText("+91 9876543210")
        c_left.addWidget(self.bulk_phone_input)

        c_right = QVBoxLayout()
        c_right.addWidget(QLabel("WhatsApp Link (Buttons Only):"))
        self.bulk_wa_input = QLineEdit()
        self.bulk_wa_input.setPlaceholderText("https://wa.me/919876543210")
        c_right.addWidget(self.bulk_wa_input)

        contact_row.addLayout(c_left)
        contact_row.addLayout(c_right)
        left_layout.addLayout(contact_row)

        layout.addWidget(left_box, 1)

        # Right Column: 4 Structures + 5th Repeater Option
        right_box = QGroupBox("Select Structure / Repeater (Vertical)")
        right_layout = QVBoxLayout(right_box)
        right_layout.setSpacing(10)

        self.bulk_struct_group = QButtonGroup(self)
        self.b_rad1 = QRadioButton(STRUCTURE_1.name)
        self.b_rad2 = QRadioButton(STRUCTURE_2.name)
        self.b_rad3 = QRadioButton(STRUCTURE_3.name)
        self.b_rad4 = QRadioButton(STRUCTURE_4.name)
        
        # 5th Repeater Option
        self.b_rad5 = QRadioButton("Option 5: Repeater Mode (Loop: Structure 1 -> 2 -> 3 -> 4 -> 1...)")
        self.b_rad5.setStyleSheet("color: #7aa2f7; font-weight: bold;")
        self.b_rad5.setChecked(True)

        self.bulk_struct_group.addButton(self.b_rad1, 1)
        self.bulk_struct_group.addButton(self.b_rad2, 2)
        self.bulk_struct_group.addButton(self.b_rad3, 3)
        self.bulk_struct_group.addButton(self.b_rad4, 4)
        self.bulk_struct_group.addButton(self.b_rad5, 5)

        right_layout.addWidget(self.b_rad1)
        right_layout.addWidget(self.b_rad2)
        right_layout.addWidget(self.b_rad3)
        right_layout.addWidget(self.b_rad4)
        right_layout.addWidget(self.b_rad5)
        right_layout.addStretch()
        layout.addWidget(right_box, 1)

        return widget

    def _create_custom_content_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Left side: Bulk Titles text box
        title_box = QVBoxLayout()
        title_header = QHBoxLayout()
        title_label = QLabel("Page Titles (1 per line for bulk posting):")
        title_label.setStyleSheet("font-weight: bold; color: #7aa2f7;")
        load_titles_btn = QPushButton("Load from File")
        load_titles_btn.setFixedWidth(110)
        load_titles_btn.clicked.connect(self._load_custom_titles_from_file)
        title_header.addWidget(title_label)
        title_header.addStretch()
        title_header.addWidget(load_titles_btn)
        title_box.addLayout(title_header)

        self.custom_titles_text = QPlainTextEdit()
        self.custom_titles_text.setPlaceholderText("Enter titles here (one per line):\nTitle 1\nTitle 2\nTitle 3\n...")
        self.custom_titles_text.setFixedHeight(105)
        title_box.addWidget(self.custom_titles_text)

        # Right side: Phone & WhatsApp
        contact_box = QVBoxLayout()
        contact_box.setSpacing(6)

        phone_box = QVBoxLayout()
        phone_lbl = QLabel("Phone Number (Call Button):")
        phone_lbl.setStyleSheet("font-weight: bold;")
        phone_box.addWidget(phone_lbl)
        self.custom_phone_input = QLineEdit()
        self.custom_phone_input.setPlaceholderText("+91 9876543210")
        phone_box.addWidget(self.custom_phone_input)

        wa_box = QVBoxLayout()
        wa_lbl = QLabel("WhatsApp Link:")
        wa_lbl.setStyleSheet("font-weight: bold;")
        wa_box.addWidget(wa_lbl)
        self.custom_wa_input = QLineEdit()
        self.custom_wa_input.setPlaceholderText("https://wa.me/919876543210")
        wa_box.addWidget(self.custom_wa_input)

        contact_box.addLayout(phone_box)
        contact_box.addLayout(wa_box)

        top_row.addLayout(title_box, 3)
        top_row.addLayout(contact_box, 2)
        layout.addLayout(top_row)

        editor_lbl = QLabel("Custom Content (Single Text Box below buttons):")
        editor_lbl.setStyleSheet("font-weight: bold; color: #7aa2f7; margin-top: 4px;")
        layout.addWidget(editor_lbl)

        # Native Rich Text Editor
        self.rich_editor_view = RichTextEditorWidget(self)
        layout.addWidget(self.rich_editor_view, 1)

        return widget

    def _load_custom_titles_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Titles Text File", "", "Text Files (*.txt)")
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self.custom_titles_text.setPlainText(content)
            count = len([k for k in content.splitlines() if k.strip()])
            QMessageBox.information(self, "Titles Loaded", f"Loaded {count} titles from file.")


    def _create_console_view(self) -> QWidget:
        style = QApplication.style()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 4, 0, 0)

        status_row = QHBoxLayout()
        self.status_label = QLabel("Ready. Select mode and click Start Task.")
        self.status_label.setStyleSheet("color: #7aa2f7; font-weight: bold;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(220)

        clear_btn = QPushButton("Clear Log")
        clear_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        clear_btn.setFixedWidth(100)
        clear_btn.clicked.connect(self._clear_log)

        open_urls_btn = QPushButton("Open URLs Folder")
        open_urls_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        open_urls_btn.setFixedWidth(150)
        open_urls_btn.clicked.connect(self._open_urls_folder)

        status_row.addWidget(self.status_label)
        status_row.addStretch()
        status_row.addWidget(open_urls_btn)
        status_row.addWidget(clear_btn)
        status_row.addWidget(self.progress_bar)
        layout.addLayout(status_row)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #101116; color: #a9b1d6; font-family: 'Consolas', monospace; font-size: 12px;")
        layout.addWidget(self.log_console)

        # Bottom row below Log Console (right side corner checkbox)
        console_bottom_row = QHBoxLayout()
        console_bottom_row.setContentsMargins(0, 2, 0, 2)
        console_bottom_row.addStretch()

        self.headless_cb = QCheckBox("Run in Background")
        self.headless_cb.setStyleSheet("color: #7aa2f7; font-weight: bold; font-size: 12px; padding: 2px 4px;")
        self.headless_cb.setToolTip("Check this to run Chrome silently in the background without opening a visible browser window.")
        saved_headless = get_setting("headless_mode", "false").lower() == "true"
        self.headless_cb.setChecked(saved_headless)
        self.headless_cb.toggled.connect(self._on_headless_toggled)
        console_bottom_row.addWidget(self.headless_cb)

        layout.addLayout(console_bottom_row)

        return widget

    def _on_headless_toggled(self, checked: bool):
        set_setting("headless_mode", "true" if checked else "false")

    def _clear_log(self):
        self.log_console.clear()

    def _open_urls_folder(self):
        urls_dir = os.path.join(BASE_DIR, "urls")
        os.makedirs(urls_dir, exist_ok=True)
        os.startfile(urls_dir)

    def _open_image_upload_dialog(self):
        dlg = ImageUploadDialog(self)
        dlg.exec()

    def _load_keywords_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Keywords Text File", "", "Text Files (*.txt)")
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self.bulk_kw_text.setPlainText(content)
            count = len([k for k in content.splitlines() if k.strip()])
            QMessageBox.information(self, "Keywords Loaded", f"Loaded {count} keywords from file.")

    def log(self, message: str):
        self.log_console.append(message)
        sb = self.log_console.verticalScrollBar()
        sb.setValue(sb.maximum())

    def start_task(self):
        mode_idx = self.stack.currentIndex()
        if mode_idx == 0:
            # Single
            mode = "single"
            kw = self.single_kw_input.text().strip()
            if not kw:
                QMessageBox.warning(self, "Missing Keyword", "Please enter a target keyword.")
                return
            keywords = [kw]
            phone = self.single_phone_input.text().strip()
            wa = self.single_wa_input.text().strip()
            struct_id = f"str-{self.single_struct_group.checkedId()}"
            is_repeater = False
            custom_content = ""

        elif mode_idx == 1:
            # Bulk
            mode = "bulk"
            lines = self.bulk_kw_text.toPlainText().splitlines()
            keywords = [line.strip() for line in lines if line.strip()]
            if not keywords:
                QMessageBox.warning(self, "Missing Keywords", "Please enter or load keywords for bulk posting.")
                return
            phone = self.bulk_phone_input.text().strip()
            wa = self.bulk_wa_input.text().strip()
            selected_id = self.bulk_struct_group.checkedId()
            if selected_id == 5:
                is_repeater = True
                struct_id = "str-1"
            else:
                is_repeater = False
                struct_id = f"str-{selected_id}"
            custom_content = ""

        else:
            # Custom
            mode = "custom"
            lines = self.custom_titles_text.toPlainText().splitlines()
            titles = [t.strip() for t in lines if t.strip()]
            if not titles:
                QMessageBox.warning(self, "Missing Titles", "Please enter at least one title for custom posting.")
                return
            keywords = titles
            phone = self.custom_phone_input.text().strip()
            wa = self.custom_wa_input.text().strip()
            struct_id = "str-custom"
            is_repeater = False
            custom_content = self.rich_editor_view.get_plain_text().strip()
            if not custom_content:
                custom_content = self.rich_editor_view.get_content().strip()
            if not custom_content:
                QMessageBox.warning(self, "Missing Content", "Please enter content in the editor box below.")
                return

        # UI state updates
        self.start_task_btn.setEnabled(False)
        self.stop_task_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log(f"[TASK START] Launching {mode.upper()} task ({len(keywords)} item(s))...")

        theme_name = self.theme_combo.currentText().strip()
        enable_announcement = self.announcement_cb.isChecked()
        headless = self.headless_cb.isChecked()

        # Start QThread Worker
        self.worker = PostingWorker(
            mode=mode,
            keywords=keywords,
            structure_id=struct_id,
            phone_number=phone,
            whatsapp_link=wa,
            is_repeater=is_repeater,
            custom_content=custom_content,
            theme_name=theme_name,
            theme_color_hex=None,
            enable_announcement=enable_announcement,
            banner_color=None,
            headless=headless,
            parent=self
        )
        self.worker.log_signal.connect(self.log)
        self.worker.status_signal.connect(self.status_label.setText)
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.url_published_signal.connect(self._on_url_published)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, current: int, total: int):
        pct = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(pct)

    def _on_url_published(self, keyword: str, url: str):
        self.log(f"[PUBLISHED] {keyword} -> {url}")

    def _on_finished(self, success: bool, message: str):
        self.start_task_btn.setEnabled(True)
        self.stop_task_btn.setEnabled(False)
        self.status_label.setText(message)
        if success:
            QMessageBox.information(self, "Task Finished", message)
        else:
            QMessageBox.warning(self, "Task Finished", message)

    def stop_task(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.stop_task_btn.setEnabled(False)
            self.status_label.setText("Stopping task...")
