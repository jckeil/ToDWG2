# -*- coding: utf-8 -*-
"""Смоук собранного exe: главное окно появляется и закрывается по WM_CLOSE."""
import os
import subprocess
import sys
import time

import win32con
import win32gui

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, 'dist', 'ToDWG_v2.0-beta.exe')
TITLE = 'ToDWG v2.'

if not os.path.isfile(EXE):
    print('нет exe:', EXE)
    sys.exit(1)

proc = subprocess.Popen([EXE])
hwnd = 0
deadline = time.time() + 30
while time.time() < deadline and proc.poll() is None:
    found = []

    def cb(h, _):
        if win32gui.IsWindowVisible(h) and TITLE in win32gui.GetWindowText(h):
            found.append(h)

    win32gui.EnumWindows(cb, None)
    if found:
        hwnd = found[0]
        break
    time.sleep(0.2)

print('окно найдено:', hwnd, 'pid:', proc.pid)
if not hwnd:
    proc.kill()
    sys.exit(1)

win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
try:
    proc.wait(timeout=15)
except subprocess.TimeoutExpired:
    proc.kill()
    print('FAIL: окно не закрылось')
    sys.exit(1)

print('процесс завершён, код', proc.returncode)
sys.exit(0)
