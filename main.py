"""
Entry Point for Google Sites Automated Poster Suite.
Equipped with Hardware-Locked License Gate & Anti-Tamper Protection.
"""

import sys
import os
import logging

# Ensure project root is in sys.path
from core.path_helper import get_base_dir
PROJECT_ROOT = get_base_dir()
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import QApplication, QDialog
from ui.main_window import MainWindow
from ui.activation_dialog import ActivationDialog
from core.security.license_guard import LicenseGuard

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )

def ensure_environment():
    """Ensure required subdirectories exist."""
    base_dirs = [
        os.path.join(PROJECT_ROOT, "urls"),
        os.path.join(PROJECT_ROOT, "chrome_profile"),
        os.path.join(PROJECT_ROOT, "images", "str-image1"),
        os.path.join(PROJECT_ROOT, "images", "str-image2"),
        os.path.join(PROJECT_ROOT, "images", "str-image3"),
        os.path.join(PROJECT_ROOT, "images", "str-image4")
    ]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)

def main():
    setup_logging()
    ensure_environment()

    app = QApplication(sys.argv)
    app.setApplicationName("Google Sites Automated Poster")
    app.setOrganizationName("AutoPoster")

    # 1. License Check: If already activated on this machine, launch directly!
    is_valid, msg = LicenseGuard.check_local_activation()
    if not is_valid:
        # Prompt user with Activation Dialog (Displays HWID and input for License Key)
        dialog = ActivationDialog()
        if dialog.exec() != QDialog.Accepted:
            # User cancelled or closed dialog without activating
            sys.exit(0)

    # 2. Launch Main Tool once activated
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
