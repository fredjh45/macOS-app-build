"""
Modern Dark CSS (QSS) stylesheet for Google Sites Poster desktop application.
"""

DARK_STYLESHEET = """
/* Global Window & Fonts */
QMainWindow, QWidget {
    background-color: #1a1b26;
    color: #c0caf5;
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}

/* Tab Bar */
QTabWidget::pane {
    border: 1px solid #292e42;
    background: #1a1b26;
    border-radius: 6px;
}

QTabBar::tab {
    background: #16161e;
    color: #7aa2f7;
    padding: 10px 24px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
    font-size: 14px;
}

QTabBar::tab:selected {
    background: #24283b;
    color: #7aa2f7;
    border-bottom: 2px solid #7aa2f7;
}

QTabBar::tab:hover {
    background: #292e42;
    color: #bb9af7;
}

/* Ribbons and Group Boxes */
QGroupBox {
    border: 1px solid #292e42;
    border-radius: 8px;
    margin-top: 14px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
    color: #bb9af7;
    background-color: #1f2335;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    background-color: #1a1b26;
}

/* Buttons */
QPushButton {
    background-color: #2ac3de;
    color: #15161e;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #7dcfff;
}

QPushButton:pressed {
    background-color: #0db9d7;
}

QPushButton:disabled {
    background-color: #414868;
    color: #787c99;
}

/* Action Buttons */
QPushButton#start_btn {
    background-color: #9ece6a;
    color: #15161e;
    font-size: 14px;
    font-weight: bold;
    padding: 10px 22px;
}

QPushButton#start_btn:hover {
    background-color: #b9f27c;
}

QPushButton#stop_btn {
    background-color: #f7768e;
    color: #15161e;
    font-size: 14px;
    font-weight: bold;
    padding: 10px 22px;
}

QPushButton#stop_btn:hover {
    background-color: #ff9eaf;
}

QPushButton#ribbon_mode_btn {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #414868;
    border-radius: 6px;
    padding: 8px 18px;
}

QPushButton#ribbon_mode_btn:checked {
    background-color: #7aa2f7;
    color: #15161e;
    font-weight: bold;
}

/* Inputs & Text Edits */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
    background-color: #16161e;
    border: 1px solid #414868;
    border-radius: 6px;
    padding: 7px 10px;
    color: #c0caf5;
    selection-background-color: #7aa2f7;
    selection-color: #15161e;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #7aa2f7;
    background-color: #1a1b26;
}

/* Radio Buttons */
QRadioButton {
    color: #c0caf5;
    spacing: 8px;
    font-size: 13px;
    padding: 4px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #565f89;
    background: #16161e;
}

QRadioButton::indicator:checked {
    border-color: #7aa2f7;
    background-color: #7aa2f7;
}

/* Progress Bar */
QProgressBar {
    background-color: #16161e;
    border: 1px solid #292e42;
    border-radius: 6px;
    height: 16px;
    text-align: center;
    color: #c0caf5;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #7aa2f7;
    border-radius: 5px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #16161e;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #414868;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #7aa2f7;
}
"""
