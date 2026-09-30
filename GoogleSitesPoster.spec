# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

datas = []
binaries = []
hiddenimports = [
    'core',
    'core.path_helper',
    'core.worker',
    'core.sites_engine',
    'core.location_helper',
    'core.structures',
    'core.structures.structure_1',
    'core.structures.structure_2',
    'core.structures.structure_3',
    'core.structures.structure_4',
    'core.structures.structure_custom',
    'core.security',
    'core.security.hwid',
    'core.security.crypto_util',
    'core.security.supabase_client',
    'core.security.license_guard',
    'ui',
    'ui.main_window',
    'ui.post_tab',
    'ui.settings_tab',
    'ui.editor_view',
    'ui.activation_dialog',
    'database',
    'database.db',
    'requests',
    'urllib3',
    'sqlite3',
    'winreg',
    'ctypes',
    'ctypes.wintypes'
]

# Collect Playwright driver and packages
tmp_ret = collect_all('playwright')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Collect PySide6 packages and plugins
tmp_ret2 = collect_all('PySide6')
datas += tmp_ret2[0]
binaries += tmp_ret2[1]
hiddenimports += tmp_ret2[2]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'test'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GoogleSitesPoster',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No black CMD console window; clean native GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
