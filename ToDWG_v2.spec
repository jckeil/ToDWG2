# -*- mode: python ; coding: utf-8 -*-

# ToDWG v2.0 (beta) — один exe, без внешних файлов рядом.
# Иконка вшивается в ресурсы и извлекается через sys._MEIPASS.
# tkinterdnd2 несёт бинарники tkdnd — их нужно включить в сборку.

from PyInstaller.utils.hooks import collect_data_files

dnd_datas = collect_data_files('tkinterdnd2')

a = Analysis(
    ['ToDWG_v2.py'],
    pathex=[],
    binaries=[],
    datas=[('Logo_toDWG.ico', '.')] + dnd_datas,
    hiddenimports=[
        'ctypes.wintypes',
        'keyboard',
        'pyperclip',
        'win32timezone',
        'win32gui',
        'win32con',
        'win32api',
        'win32com',
        'win32com.client',
        'pythoncom',
        'ezdxf',
        'ezdxf.xref',
        'ezdxf.bbox',
        'tkinterdnd2',
        'tkinterdnd2.TkinterDnD',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ToDWG_v2.0-beta',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Logo_toDWG.ico'],
)
