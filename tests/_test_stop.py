"""Локальная проверка экстренной остановки и вспомогательных функций."""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ToDWG_v2 as m

m.init_log()
ok = []

# 1. pause прерывается мгновенно.
m.STOP_EVENT.clear()
threading.Timer(0.2, m.STOP_EVENT.set).start()
t0 = time.time()
try:
    m.pause(5.0)
    ok.append("FAIL pause: не прервался")
except m.TaskStopped:
    dt = time.time() - t0
    ok.append(f"pause прерван за {dt:.2f} с " + ("OK" if dt < 0.4 else "FAIL"))

# 2. wait_file_created прерывается (раньше ждал 10 секунд).
m.STOP_EVENT.clear()
threading.Timer(0.2, m.STOP_EVENT.set).start()
t0 = time.time()
try:
    m.wait_file_created(os.path.join(m.BASE_DIR, "_нет_такого.dxf"), timeout=10.0)
    ok.append("FAIL wait_file_created: не прервался")
except m.TaskStopped:
    dt = time.time() - t0
    ok.append(f"wait_file_created прерван за {dt:.2f} с "
              + ("OK" if dt < 0.5 else "FAIL"))

# 3. find_save_dialog прерывается.
m.STOP_EVENT.clear()
threading.Timer(0.2, m.STOP_EVENT.set).start()
t0 = time.time()
try:
    m.find_save_dialog(timeout=8.0)
    ok.append("FAIL find_save_dialog: не прервался")
except m.TaskStopped:
    dt = time.time() - t0
    ok.append(f"find_save_dialog прерван за {dt:.2f} с "
              + ("OK" if dt < 0.5 else "FAIL"))

# 4. stop_suspended: внутри него остановка не мешает.
m.STOP_EVENT.set()
try:
    with m.stop_suspended():
        m.pause(0.3)
    ok.append("stop_suspended OK")
except m.TaskStopped:
    ok.append("FAIL stop_suspended: прервался")

# 5. confirm_dialog на неверном hwnd не падает.
m.STOP_EVENT.clear()
try:
    r = m.confirm_dialog(0)
    ok.append(f"confirm_dialog(0) -> {r} OK")
except Exception as e:
    ok.append(f"FAIL confirm_dialog: {e}")

# 6. process_windows / window_pid не падают.
try:
    ok.append(f"window_pid(0)={m.window_pid(0)} "
              f"process_windows={len(m.process_windows(m.window_pid(0)))} OK")
except Exception as e:
    ok.append(f"FAIL process_windows: {e}")

# 7. Системная регистрация горячей клавиши + эмуляция нажатия.
m.STOP_EVENT.clear()
m.start_stop_hotkey()
time.sleep(1.0)
ok.append(f"RegisterHotKey: {m._HOTKEY['registered']}")
try:
    import keyboard
    for how in ("keyboard.send", "keybd_event"):
        if m.STOP_EVENT.is_set():
            break
        if how == "keyboard.send":
            keyboard.send("ctrl+alt+0")
        else:
            import ctypes
            KEYEVENTF_KEYUP = 0x0002
            VK_CONTROL, VK_MENU, VK_0 = 0x11, 0x12, 0x30
            for vk in (VK_CONTROL, VK_MENU, VK_0):
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
            for vk in (VK_0, VK_MENU, VK_CONTROL):
                ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        for _ in range(40):
            if m.STOP_EVENT.is_set():
                break
            time.sleep(0.05)
        ok.append(f"  {how}: " + ("OK" if m.STOP_EVENT.is_set() else "нет"))
        m.STOP_EVENT.clear()
    ok.append(f"сообщений в потоке хоткея: {m._HOTKEY.get('messages', 0)}")
except Exception as e:
    ok.append(f"хоткей: ошибка {e}")

# 8. Проверка GW_OWNER и confirm_dialog на реальном окне класса #32770.
try:
    import win32con
    import win32gui
    print("GW_OWNER =", win32con.GW_OWNER)
    dlg = win32gui.CreateWindowEx(0, "#32770", "Сохранение", win32con.WS_OVERLAPPEDWINDOW,
                                  0, 0, 300, 200, 0, 0, 0, None)
    print("создан #32770:", dlg, "заголовок:", repr(win32gui.GetWindowText(dlg)))
    print("find_save_dialog находит:", m.find_save_dialog(timeout=0.5) == dlg)
    t0 = time.time()
    r = m.confirm_dialog(dlg, note="тест", timeout=0.4)
    print(f"confirm_dialog -> {r} за {time.time() - t0:.2f} с (ожидается False)")
    if win32gui.IsWindow(dlg):
        win32gui.DestroyWindow(dlg)
except Exception as e:
    print("тест диалога: ошибка", e)

m._PIPELINE_STATE["running"] = False
for line in ok:
    print(line)
