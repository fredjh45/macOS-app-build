"""
Central Path Resolution Helper.
Accurately resolves external assets (images/, chrome_profile/, urls/, poster_app.db)
whether running from Python source or as a compiled PyInstaller .exe binary.
"""

import os
import sys

def get_base_dir() -> str:
    """
    Returns the real base directory of the application:
    - If running as compiled .exe: returns directory containing the .exe file.
    - If running as compiled macOS .app: returns directory containing the .app bundle.
    - If running from source: returns project root directory.
    """
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
        if sys.platform == 'darwin' and '.app/Contents/MacOS' in exe_path:
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(exe_path))))
        return os.path.dirname(exe_path)
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(cur_dir)

def get_app_data_dir() -> str:
    """
    Returns writable directory for dynamic database, chrome profile, and license.
    On macOS: uses ~/Library/Application Support/GoogleSitesPoster
    On Windows: uses base directory alongside .exe
    """
    if sys.platform == "darwin":
        path = os.path.expanduser("~/Library/Application Support/GoogleSitesPoster")
        os.makedirs(path, exist_ok=True)
        return path
    return get_base_dir()

def get_images_dir() -> str:
    local_images = os.path.join(get_base_dir(), "images")
    if os.path.exists(local_images):
        return local_images
    data_images = os.path.join(get_app_data_dir(), "images")
    os.makedirs(data_images, exist_ok=True)
    return data_images

def get_profile_dir() -> str:
    return os.path.join(get_app_data_dir(), "chrome_profile")

def get_urls_dir() -> str:
    return os.path.join(get_app_data_dir(), "urls")

def get_db_path() -> str:
    return os.path.join(get_app_data_dir(), "poster_app.db")

def get_license_file_path() -> str:
    return os.path.join(get_profile_dir(), ".license.dat")
