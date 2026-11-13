# -*- coding: utf-8 -*-
"""Проверка починки «битых» DXF Schemagee (сырые переводы строк).

Schemagee пишет многострочный текст без экранирования: после кода группы
идёт пустая строка, затем продолжение. ezdxf такой файл не читает
(«Invalid group code»), поэтому read_dxf() правит текст перед разбором.
"""
import glob
import os
import sys
import tempfile

import ezdxf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ToDWG_v2 as m

m.init_log()

BROKEN = ("0\nSECTION\n2\nENTITIES\n0\nTEXT\n1\n\nсерый ITK\n"
          "41\n0.9\n0\nENDSEC\n0\nEOF\n")

fixed, n = m._repair_dxf_text(BROKEN)
print("синтетика: исправлений", n)
assert n == 1, n
assert "серый ITK" in fixed

folder = os.path.join(m.BASE_DIR, "input")
files = sorted(glob.glob(os.path.join(folder, "*.dxf")))
print("файлов в input:", len(files))

encodings = {}
for path in files:
    enc = m._dxf_encoding(path)
    encodings[enc] = encodings.get(enc, 0) + 1
print("кодировки:", encodings)

bad = []
for path in files:
    try:
        doc = m.read_dxf(path)
        if not list(doc.modelspace()):
            bad.append((os.path.basename(path), "пустой modelspace"))
    except Exception as e:
        bad.append((os.path.basename(path), str(e)[:80]))

for name, err in bad:
    print("  PROBLEM:", name, "-", err)

# Пустой DXF не должен считаться сохранённым листом.
empty_path = os.path.join(tempfile.gettempdir(), "ToDWG_empty.dxf")
ezdxf.new("R2018").saveas(empty_path)
empty_ok = m._dxf_has_content(empty_path) is False
print("пустой DXF отклонён:", empty_ok)
if not empty_ok:
    bad.append(("_dxf_has_content", "пустой DXF принят за успех"))

# DXF в UTF-8 (R2018) должен читаться без порчи русского текста.
utf_path = os.path.join(tempfile.gettempdir(), "ToDWG_utf8.dxf")
utf_doc = ezdxf.new("R2018")
utf_doc.modelspace().add_text("Проверка шрифта", dxfattribs={"height": 2.5})
utf_doc.saveas(utf_path)
utf_enc = m._dxf_encoding(utf_path)
utf_text = [e.dxf.text for e in m.read_dxf(utf_path).modelspace().query("TEXT")]
print("UTF-8 DXF: кодировка", utf_enc, "текст", utf_text)
if utf_enc != "utf-8" or utf_text != ["Проверка шрифта"]:
    bad.append(("utf-8", f"{utf_enc}: {utf_text}"))

content_ok = all(m._dxf_has_content(p) for p in files)
print("_dxf_has_content для всех файлов:", content_ok)
if not content_ok:
    bad.append(("_dxf_has_content", "есть файлы без содержимого"))

print("ИТОГ:", "OK" if not bad else "FAIL")
sys.exit(0 if not bad else 1)
