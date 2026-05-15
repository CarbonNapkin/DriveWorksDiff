# PyInstaller spec for DriveWorks Project Compare.
#
# Produces a single-file, windowed executable. The Windows file-properties
# version block is filled in from the version string in dw_compare/__init__.py.
# Drives both Mac and Windows builds; PyInstaller picks the right output
# format for the host platform (`.exe` on Windows, `.app` on macOS).
#
# Usage:
#   pyinstaller dw_compare.spec --clean --noconfirm
#
# Optional icon files (skipped silently if absent):
#   assets/icon.ico  (Windows)
#   assets/icon.icns (macOS)

import os
import sys

# Pull version directly from the package without importing the whole thing.
_version = '1.0.0'
_init_path = os.path.join(os.path.dirname(SPEC), 'dw_compare', '__init__.py')
with open(_init_path, 'r', encoding='utf-8') as fh:
    for line in fh:
        if line.strip().startswith('__version__'):
            _version = line.split('=', 1)[1].strip().strip('\'"')
            break

block_cipher = None

icon_ico = os.path.join('assets', 'icon.ico')
icon_icns = os.path.join('assets', 'icon.icns')
chosen_icon = None
if sys.platform == 'win32' and os.path.isfile(icon_ico):
    chosen_icon = icon_ico
elif sys.platform == 'darwin' and os.path.isfile(icon_icns):
    chosen_icon = icon_icns

a = Analysis(
    ['run_dw_compare.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['dw_compare.gui'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    name='DriveWorksDiff',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=chosen_icon,
    version=None,
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='DriveWorksDiff.app',
        icon=chosen_icon,
        bundle_identifier='com.base10consultants.driveworksdiff',
        info_plist={
            'CFBundleShortVersionString': _version,
            'CFBundleVersion': _version,
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
        },
    )
