# -*- coding: utf-8 -*-
"""Проверка кодировки: DXF Schemagee (R12, cp1251) читаются без мусора.

Schemagee пишет R12 (AC1009) без $DWGCODEPAGE; ezdxf.readfile() берёт для
такого файла cp1252 и превращает кириллицу в «Êîïèðîâàë:». Проверяем,
что read_dxf() читает текст правильно и что он остаётся верным после
сборки альбома.
"""
import glob
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ToDWG_v2 as m

m.init_log()


def texts(path):
    doc = m.read_dxf(path)
    return [e.dxf.text for e in doc.modelspace().query("TEXT")]


def main():
    folder = os.path.join(m.BASE_DIR, "input")
    files = sorted(glob.glob(os.path.join(folder, "*.dxf")))
    print("файлов:", len(files))
    if not files:
        print("FAIL: нет DXF в input")
        return 1

    bad = []
    for path in files:
        joined = " ".join(texts(path))
        if "Формат" not in joined and "Копировал" not in joined:
            bad.append((os.path.basename(path), joined[:80]))

    tmp = tempfile.mkdtemp(prefix="ToDWG_enc_")
    try:
        src = os.path.join(tmp, "src")
        os.makedirs(src)
        for path in files[:2]:
            shutil.copy2(path, src)
        result = m.merge_all(src, os.path.join(tmp, "out"), name="enc",
                             make_dwg=False)
        joined = " ".join(texts(result["file"]))
        merged_ok = "Формат" in joined and "Êîïèðîâàë" not in joined
        print("альбом собран:", result["file"])
        print("текст в альбоме верный:", merged_ok)
        if not merged_ok:
            bad.append(("альбом", joined[:80]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for name, sample in bad:
        print("  PROBLEM:", name, "-", sample)

    print("ИТОГ:", "OK" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
