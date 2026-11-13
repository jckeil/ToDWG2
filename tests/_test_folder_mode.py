# -*- coding: utf-8 -*-
"""Проверки новых функций v2.0: папка (задача 3) и проверка доступности (задача 2)."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ToDWG_v2 as m   # noqa: E402

fails = []


def check(name, cond, extra=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{extra}]" if extra else ""))
    if not cond:
        fails.append(name)


def main():
    root = tempfile.mkdtemp(prefix="ToDWG_test_")

    # --- unique_path: имя, (2), (3) -------------------------------------
    open(os.path.join(root, "a.dwg"), "w").close()
    open(os.path.join(root, "a (2).dwg"), "w").close()
    p3 = m.unique_path(root, "a", ".dwg")
    check("unique_path -> a (3).dwg", os.path.basename(p3) == "a (3).dwg", p3)
    free = m.unique_path(root, "b", ".dwg")
    check("unique_path свободное имя", os.path.basename(free) == "b.dwg", free)

    # --- find_sdd_recursive: рекурсивный поиск, сортировка --------------
    sub = os.path.join(root, "sub", "deep")
    os.makedirs(sub)
    for name in ("b.sdd", os.path.join("sub", "a.sdd"),
                 os.path.join("sub", "deep", "c.sdd")):
        full = os.path.join(root, name)
        open(full, "w").close()
    open(os.path.join(root, "ignore.txt"), "w").close()
    open(os.path.join(root, "sub", "x.SDD"), "w").close()   # регистр расширения
    found = m.find_sdd_recursive(root)
    names = sorted(os.path.basename(x) for x in found)
    check("find_sdd_recursive нашёл все .sdd (вкл. .SDD)",
          names == ["a.sdd", "b.sdd", "c.sdd", "x.SDD"], str(names))
    check("find_sdd_recursive отсортирован",
          found == sorted(found, key=lambda p: p.lower()))

    # --- relocate_result: перенос рядом с исходником + суффикс ----------
    work = tempfile.mkdtemp(prefix="ToDWG_work_")
    produced = os.path.join(work, "doc.dwg")
    with open(produced, "wb") as f:
        f.write(b"DWG")
    dest = m.relocate_result({"target": produced}, root)
    check("relocate_result перенёс файл", dest and os.path.isfile(dest), dest)
    check("relocate_result имя doc.dwg", os.path.basename(dest) == "doc.dwg")
    check("relocate_result исходник удалён (move)", not os.path.isfile(produced))

    with open(os.path.join(work, "doc.dwg"), "wb") as f:
        f.write(b"DWG2")
    dest2 = m.relocate_result({"target": os.path.join(work, "doc.dwg")}, root)
    check("relocate_result суффикс (2)", os.path.basename(dest2) == "doc (2).dwg",
          dest2)

    # --- probe_path: локальная папка доступна --------------------------
    ok, err = m.probe_path(root, need_write=True)
    check("probe_path локальная папка ok", ok, err)
    check("probe_path не оставляет пробный файл",
          not [n for n in os.listdir(root) if n.startswith(".ToDWG_probe_")])

    missing = os.path.join(root, "no_such_dir")
    ok2, err2 = m.probe_path(missing, need_write=True)
    check("probe_path отсутствующая папка -> ошибка", not ok2, err2)
    check("probe_path текст ошибки понятен", "не найдена" in err2.lower(), err2)

    # --- probe_path: недоступный сетевой путь -> таймаут/ошибка --------
    # 192.0.2.0/24 — TEST-NET-1 (RFC 5737), заведомо недостижим.
    net = r"\\192.0.2.1\share"
    ok3, err3 = m.probe_path(net, timeout=2.0, need_write=True)
    check("probe_path недоступная сеть -> ошибка", not ok3, err3)

    print("\nИТОГ:", "OK" if not fails else f"FAIL ({len(fails)})")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
