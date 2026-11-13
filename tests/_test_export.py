"""Проверка нажатия «Экспорт» в модальном окне Schemagee.

Проверяем то, из-за чего листы не сохранялись: после диалога «Сохранение»
нужно нажать кнопку в форме экспорта (в старом кликере — Tab+Enter).
"""
import ctypes
import os
import sys
import tempfile
import threading
import time
import tkinter as tk

import win32con
import win32gui

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ToDWG_v2 as m

m.init_log()
results = []


def find_by_title(title, timeout=3.0):
    end = time.time() + timeout
    while time.time() < end:
        found = []

        def cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd) and \
                    win32gui.GetWindowText(hwnd) == title:
                found.append(hwnd)

        win32gui.EnumWindows(cb, None)
        if found:
            return found[0]
        time.sleep(0.05)
    return 0


root = tk.Tk()
root.title("main")
root.geometry("160x80+20+20")
root.update()
main_hwnd = ctypes.windll.user32.GetParent(root.winfo_id())

# 1. Диалог «Сохранение» НЕ должен приниматься за форму экспорта.
state = {}


def show_save():
    state["save"] = ctypes.windll.user32.MessageBoxW(
        None, "Сохранить файл?", "Сохранение", 0x00000000)


th = threading.Thread(target=show_save, daemon=True)
th.start()
dlg = find_by_title("Сохранение")
if not dlg:
    results.append("FAIL: тестовый диалог «Сохранение» не появился")
else:
    r = m.press_export_button(main_hwnd, look=1.0)
    still = bool(win32gui.IsWindow(dlg))
    results.append(("_export_form пропускает диалог сохранения OK"
                    if (not r and still) else
                    f"FAIL: диалог сохранения обработан как форма (r={r})"))
    win32gui.PostMessage(dlg, win32con.WM_COMMAND, win32con.IDOK, 0)
th.join(3.0)

# 2. Форма экспорта: кнопка находится по тексту и нажимается без фокуса.
state = {}


def show_export():
    state["export"] = ctypes.windll.user32.MessageBoxW(
        None, "Экспорт в DXF", "Экспорт в DXF", 0x00000000)


th = threading.Thread(target=show_export, daemon=True)
th.start()
dlg = find_by_title("Экспорт в DXF")
if not dlg:
    results.append("FAIL: тестовый диалог «Экспорт в DXF» не появился")
else:
    button = m._find_button(dlg, m.EXPORT_BUTTON_TEXTS)
    text = win32gui.GetWindowText(button) if button else ""
    results.append("кнопка по тексту найдена OK" if button
                   else "FAIL: кнопка экспорта не найдена")
    results.append("несовпадающий текст не нажимается OK"
                   if m._find_button(dlg, ("ЭкспортX", "Совсем другое")) == 0
                   else "FAIL: _find_button нажал кнопку без совпадения")
    t0 = time.time()
    r = m.press_export_button(main_hwnd, look=2.0)
    dt = time.time() - t0
    results.append(("форма экспорта подтверждена за %.2f с OK" % dt
                    if r and not win32gui.IsWindow(dlg) else
                    f"FAIL: форма не закрыта (r={r}, кнопка={text!r})"))
th.join(3.0)
results.append("поток диалога завершён OK" if not th.is_alive()
               else "FAIL: поток диалога не завершился")
results.append(f"код, который вернул диалог: {state.get('export')}")

# 3. Без главного окна функция не падает и не нажимает ничего.
results.append("press_export_button(0) = False OK"
               if m.press_export_button(0, look=0.3) is False else
               "FAIL: press_export_button(0) вернул не False")

root.destroy()

lines = list(results)
lines.append("ИТОГ: " + ("OK" if not any(x.startswith("FAIL") for x in results)
                         else "ЕСТЬ ОШИБКИ"))
with open(os.path.join(tempfile.gettempdir(), "ToDWG_test_export.txt"),
          "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
for line in lines:
    print(line)
