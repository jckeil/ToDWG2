# -*- coding: utf-8 -*-
"""Тест интерфейса: строит главное окно и опрашивает виджеты."""
import os
import sys
import tempfile

import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ToDWG_v2 as app

report = []


def mainloop_stub(self, n=0):
    def walk(w):
        yield w
        for c in w.winfo_children():
            yield from walk(c)

    check = None
    format_check = None
    spin = None
    combos = []
    buttons = []
    checks = []
    for w in walk(self):
        try:
            if isinstance(w, tk.Label):
                text = w.cget("text")
                if text:
                    report.append(("label", text))
            elif isinstance(w, tk.Checkbutton):
                text = w.cget("text")
                checks.append(text)
                if text == "Указать количество листов вручную":
                    check = w
                if text.startswith("Выбрать формат листа вручную"):
                    format_check = w
                report.append(("check", text, w.cget("state")))
            elif isinstance(w, tk.Spinbox):
                spin = w
                report.append(("spin", w.cget("from"), w.cget("to"),
                               w.cget("state")))
            elif isinstance(w, ttk.Combobox):
                combos.append(w)
                report.append(("combo", w.get(), w.cget("state")))
            elif isinstance(w, tk.Button):
                buttons.append(w)
                report.append(("button", w.cget("text"), w.cget("state")))
        except Exception as e:
            report.append(("error", str(e)))

    report.append(("title", self.title()))
    report.append(("geometry", self.geometry()))
    report.append(("reqheight", self.winfo_reqheight()))
    report.append(("checkboxes", ", ".join(checks)))

    self.update()
    card = self.winfo_children()[0]
    bottom = 0
    layout = []
    for child in card.winfo_children():
        text = ""
        try:
            text = str(child.cget("text"))[:24]
        except Exception:
            pass
        y = child.winfo_y()
        h = child.winfo_height()
        layout.append(f"{child.winfo_class()}:{text or '-'}@{y}+{h}")
        if text == app.APP_DISPLAY_VERSION:
            continue
        bottom = max(bottom, y + h)
    report.append(("content_bottom", bottom,
                   "card_h", card.winfo_height(),
                   "root_h", self.winfo_height()))
    report.append(("layout", " | ".join(layout)))

    canvas = None
    dark = None
    for w in walk(self):
        if isinstance(w, tk.Canvas):
            try:
                width = int(str(w.cget("width")))
            except Exception:
                width = 0
            if width == 42:
                dark = w
            else:
                canvas = w

    if canvas is not None:
        report.append(("canvas_wheel_bound",
                       bool(canvas.bind("<MouseWheel>"))))

    if dark is not None:
        style = ttk.Style()
        report.append(("theme_light", self.cget("bg"), card.cget("bg"),
                       spin.cget("bg") if spin is not None else "-",
                       style.lookup("TCombobox", "fieldbackground")))
        dark.event_generate("<Button-1>", x=5, y=5)
        self.update()
        report.append(("theme_dark", self.cget("bg"), card.cget("bg"),
                       spin.cget("bg") if spin is not None else "-",
                       spin.cget("disabledbackground")
                       if spin is not None else "-",
                       style.lookup("TCombobox", "fieldbackground")))
        dark.event_generate("<Button-1>", x=5, y=5)
        self.update()
        report.append(("theme_back", self.cget("bg"), card.cget("bg")))

    if check is not None and spin is not None:
        check.invoke()
        self.update()
        report.append(("spin_after_on", spin.cget("state")))
        report.append(("hint_after_on", spin.get()))
        check.invoke()
        self.update()
        report.append(("spin_after_off", spin.cget("state")))

    if format_check is not None and combos:
        format_check.invoke()
        self.update()
        report.append(("combo_after_on",
                       ", ".join(str(c.cget("state")) for c in combos)))
        format_check.invoke()
        self.update()
        report.append(("combo_after_off",
                       ", ".join(str(c.cget("state")) for c in combos)))

    self.destroy()


tk.Tk.mainloop = mainloop_stub
code = app.run_gui()

out_path = os.path.join(tempfile.gettempdir(), "ToDWG_gui_selftest.txt")
with open(out_path, "w", encoding="utf-8") as f:
    for item in report:
        f.write("|".join(str(x) for x in item) + "\n")
    f.write(f"EXIT_CODE={code}\n")
print(out_path)
sys.exit(0)
