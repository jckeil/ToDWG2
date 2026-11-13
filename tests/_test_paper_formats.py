# -*- coding: utf-8 -*-
"""Проверка форматов листов: A2/A3/A4 и ориентация в layout'ах альбома."""
import glob
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ToDWG_v2 as m

m.init_log()

CASES = [
    ("A2", True, 594.0, 420.0),
    ("A2", False, 420.0, 594.0),
    ("A3", True, 420.0, 297.0),
    ("A3", False, 297.0, 420.0),
    ("A4", True, 297.0, 210.0),
    ("A4", False, 210.0, 297.0),
]


def main():
    files = sorted(glob.glob(os.path.join(m.BASE_DIR, "input", "*.dxf")))[:2]
    if len(files) < 2:
        print("FAIL: нужно минимум 2 DXF в input")
        return 1

    bad = []
    for fmt, landscape, exp_w, exp_h in CASES:
        tmp = tempfile.mkdtemp(prefix="ToDWG_paper_")
        try:
            src = os.path.join(tmp, "src")
            os.makedirs(src)
            for path in files:
                shutil.copy2(path, src)
            width, height = m.paper_size(fmt, landscape)
            result = m.merge_all(src, os.path.join(tmp, "out"), name="t",
                                 make_dwg=False,
                                 paper_w=width, paper_h=height)
            doc = m.read_dxf(result["file"])
            layout = doc.layouts.get("Лист 1")
            got = (round(layout.dxf.paper_width, 1),
                   round(layout.dxf.paper_height, 1))
            ok = got == (exp_w, exp_h)
            print(f"{fmt} {'гориз' if landscape else 'верт'}: {got} "
                  f"({'OK' if ok else 'FAIL, ждали ' + str((exp_w, exp_h))})")
            if not ok:
                bad.append((fmt, landscape, got))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print("ИТОГ:", "OK" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
