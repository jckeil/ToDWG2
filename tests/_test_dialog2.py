"""Проверка: WM_COMMAND(IDOK) закрывает диалог с кнопкой id=1."""
import ctypes
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ToDWG_v2 as m
import win32gui

m.init_log()
res = {}


def worker():
    res["ret"] = ctypes.windll.user32.MessageBoxW(0, "проверка", "Сохранение",
                                                  0x00000001)  # OK/Cancel


t = threading.Thread(target=worker, daemon=True)
t.start()
d = m.find_save_dialog(timeout=4.0)
print("найден диалог:", d)
if d:
    m.dump_dialog_controls(d, "okcancel")
    t0 = time.time()
    ok = m.confirm_dialog(d, "okcancel", timeout=1.0)
    print(f"confirm_dialog: {ok} за {time.time() - t0:.2f} с")
    print("окно закрыто:", not win32gui.IsWindow(d))
t.join(3.0)
print("поток завершён:", not t.is_alive(), "код:", res)
