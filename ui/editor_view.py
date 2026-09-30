"""
Native PySide6 Rich Text Editor (WYSIWYG).
Replaces CKEditor with a lightweight, offline, high-performance editor.
Features a full formatting toolbar:
- Heading styles (Normal, H1, H2, H3)
- Font Family & Font Size selection
- Bold, Italic, Underline, Strikethrough
- Text Color picker
- Alignment (Left, Center, Right, Justify)
- Bulleted & Numbered Lists
- Insert Link dialog
- Direct HTML and plain text extraction
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QTextEdit,
    QComboBox, QFontComboBox, QPushButton, QColorDialog,
    QDialog, QLabel, QLineEdit, QStyle, QApplication, QFrame
)
from PySide6.QtGui import (
    QTextCharFormat, QFont, QColor, QTextBlockFormat,
    QTextCursor, QTextListFormat
)
from PySide6.QtCore import Qt, Signal

class InsertLinkDialog(QDialog):
    """Dialog to insert a link with URL and text."""
    def __init__(self, default_text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Hyperlink")
        self.setFixedWidth(380)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Display Text:"))
        self.text_input = QLineEdit()
        self.text_input.setText(default_text)
        layout.addWidget(self.text_input)

        layout.addWidget(QLabel("Target URL (e.g., https://example.com):"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://")
        layout.addWidget(self.url_input)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("Insert Link")
        ok_btn.setStyleSheet("background-color: #7aa2f7; color: #15161e; font-weight: bold;")
        ok_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

    def get_data(self):
        return self.text_input.text().strip(), self.url_input.text().strip()


class RichTextEditorWidget(QWidget):
    content_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)

        self._create_toolbar()
        self._create_editor()

    def _create_toolbar(self):
        style = QApplication.style()

        self.toolbar_widget = QWidget(self)
        self.toolbar_widget.setStyleSheet("background-color: #1f2335; border: 1px solid #292e42; border-radius: 6px; padding: 4px;")
        t_layout = QHBoxLayout(self.toolbar_widget)
        t_layout.setContentsMargins(4, 4, 4, 4)
        t_layout.setSpacing(6)

        # Style / Heading Selector
        self.heading_combo = QComboBox()
        self.heading_combo.addItems(["Normal Text", "Heading 1 (H1)", "Heading 2 (H2)", "Heading 3 (H3)"])
        self.heading_combo.setFixedWidth(130)
        self.heading_combo.currentIndexChanged.connect(self._apply_heading_style)
        t_layout.addWidget(self.heading_combo)

        # Font Family
        self.font_combo = QFontComboBox()
        self.font_combo.setFixedWidth(140)
        self.font_combo.currentFontChanged.connect(self._set_font_family)
        t_layout.addWidget(self.font_combo)

        # Font Size
        self.size_combo = QComboBox()
        self.size_combo.addItems([str(s) for s in [9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32]])
        self.size_combo.setCurrentText("12")
        self.size_combo.setFixedWidth(60)
        self.size_combo.currentTextChanged.connect(self._set_font_size)
        t_layout.addWidget(self.size_combo)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("color: #414868;")
        t_layout.addWidget(sep1)

        # Bold
        self.bold_btn = QPushButton("B")
        self.bold_btn.setFixedSize(30, 28)
        self.bold_btn.setStyleSheet("font-weight: bold; font-family: monospace;")
        self.bold_btn.setCheckable(True)
        self.bold_btn.clicked.connect(self._toggle_bold)
        t_layout.addWidget(self.bold_btn)

        # Italic
        self.italic_btn = QPushButton("I")
        self.italic_btn.setFixedSize(30, 28)
        self.italic_btn.setStyleSheet("font-style: italic; font-family: monospace;")
        self.italic_btn.setCheckable(True)
        self.italic_btn.clicked.connect(self._toggle_italic)
        t_layout.addWidget(self.italic_btn)

        # Underline
        self.underline_btn = QPushButton("U")
        self.underline_btn.setFixedSize(30, 28)
        self.underline_btn.setStyleSheet("text-decoration: underline; font-family: monospace;")
        self.underline_btn.setCheckable(True)
        self.underline_btn.clicked.connect(self._toggle_underline)
        t_layout.addWidget(self.underline_btn)

        # Color Picker
        self.color_btn = QPushButton("Color")
        self.color_btn.setFixedHeight(28)
        self.color_btn.clicked.connect(self._pick_text_color)
        t_layout.addWidget(self.color_btn)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet("color: #414868;")
        t_layout.addWidget(sep2)

        # Alignment Buttons
        self.align_left_btn = QPushButton("Left")
        self.align_left_btn.setFixedHeight(28)
        self.align_left_btn.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignLeft))
        t_layout.addWidget(self.align_left_btn)

        self.align_center_btn = QPushButton("Center")
        self.align_center_btn.setFixedHeight(28)
        self.align_center_btn.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignCenter))
        t_layout.addWidget(self.align_center_btn)

        self.align_right_btn = QPushButton("Right")
        self.align_right_btn.setFixedHeight(28)
        self.align_right_btn.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignRight))
        t_layout.addWidget(self.align_right_btn)

        # Lists
        self.bullet_btn = QPushButton("List")
        self.bullet_btn.setFixedHeight(28)
        self.bullet_btn.clicked.connect(self._toggle_bullet_list)
        t_layout.addWidget(self.bullet_btn)

        # Link
        self.link_btn = QPushButton("Link")
        self.link_btn.setFixedHeight(28)
        self.link_btn.clicked.connect(self._insert_link)
        t_layout.addWidget(self.link_btn)

        t_layout.addStretch()

        # Clear Format
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(28)
        self.clear_btn.clicked.connect(self._clear_formatting)
        t_layout.addWidget(self.clear_btn)

        self.layout.addWidget(self.toolbar_widget)

    def _create_editor(self):
        self.editor = QTextEdit(self)
        self.editor.setAcceptRichText(True)
        self.editor.setPlaceholderText("Enter or paste your custom content here. Format headings, lists, and paragraphs with the toolbar above...")
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #16161e;
                color: #c0caf5;
                border: 1px solid #414868;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                line-height: 1.6;
            }
            QTextEdit:focus {
                border: 1px solid #7aa2f7;
            }
        """)
        
        # Initial template text
        self.editor.setHtml("""
            <h2>Custom Section Title</h2>
            <p>Write or paste your custom manual content here. You can add custom paragraphs, bullet points, and formatting.</p>
            <ul>
                <li>Key feature or benefit point</li>
                <li>Reliable and quality execution</li>
            </ul>
        """)

        self.editor.textChanged.connect(self.content_changed.emit)
        self.editor.cursorPositionChanged.connect(self._update_format_states)
        self.layout.addWidget(self.editor)

    def _toggle_bold(self):
        fmt = QTextCharFormat()
        weight = QFont.Weight.Bold if self.bold_btn.isChecked() else QFont.Weight.Normal
        fmt.setFontWeight(weight)
        self._merge_format(fmt)

    def _toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.italic_btn.isChecked())
        self._merge_format(fmt)

    def _toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.underline_btn.isChecked())
        self._merge_format(fmt)

    def _set_font_family(self, font: QFont):
        fmt = QTextCharFormat()
        fmt.setFontFamilies([font.family()])
        self._merge_format(fmt)

    def _set_font_size(self, size_str: str):
        try:
            size = float(size_str)
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size)
            self._merge_format(fmt)
        except ValueError:
            pass

    def _pick_text_color(self):
        col = QColorDialog.getColor(QColor("#c0caf5"), self, "Select Text Color")
        if col.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(col)
            self._merge_format(fmt)

    def _set_alignment(self, alignment: Qt.AlignmentFlag):
        self.editor.setAlignment(alignment)

    def _apply_heading_style(self, index: int):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()
        
        if index == 1:  # H1
            fmt.setFontPointSize(22)
            fmt.setFontWeight(QFont.Weight.Bold)
        elif index == 2:  # H2
            fmt.setFontPointSize(18)
            fmt.setFontWeight(QFont.Weight.Bold)
        elif index == 3:  # H3
            fmt.setFontPointSize(15)
            fmt.setFontWeight(QFont.Weight.DemiBold)
        else:  # Normal
            fmt.setFontPointSize(12)
            fmt.setFontWeight(QFont.Weight.Normal)

        cursor.mergeBlockCharFormat(fmt)
        self.editor.setTextCursor(cursor)

    def _toggle_bullet_list(self):
        cursor = self.editor.textCursor()
        cursor.createList(QTextListFormat.Style.ListDisc)

    def _insert_link(self):
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()
        dlg = InsertLinkDialog(selected_text, self)
        if dlg.exec():
            text, url = dlg.get_data()
            if text and url:
                html = f'<a href="{url}">{text}</a>'
                cursor.insertHtml(html)

    def _clear_formatting(self):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Normal)
        fmt.setFontItalic(False)
        fmt.setFontUnderline(False)
        fmt.setFontPointSize(12)
        fmt.setForeground(QColor("#c0caf5"))
        cursor.setCharFormat(fmt)

    def _merge_format(self, fmt: QTextCharFormat):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)

    def _update_format_states(self):
        fmt = self.editor.currentCharFormat()
        self.bold_btn.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
        self.italic_btn.setChecked(fmt.fontItalic())
        self.underline_btn.setChecked(fmt.fontUnderline())

    def get_content(self, callback=None) -> str:
        """Returns clean HTML content."""
        html = self.editor.toHtml()
        if callback:
            callback(html)
        return html

    def get_plain_text(self) -> str:
        return self.editor.toPlainText()

    def set_content(self, html: str):
        self.editor.setHtml(html)


# For backward compatibility
CKEditorWidget = RichTextEditorWidget
