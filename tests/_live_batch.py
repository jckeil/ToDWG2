# -*- coding: utf-8 -*-
"""Живой пакетный прогон: несколько .sdd подряд, каждому — своя папка.

Использование:
    python tests\\_live_batch.py "файл1.sdd" "файл2.sdd" ...

Проверяет сценарий drag-and-drop с несколькими файлами без GUI.
"""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ToDWG_v2 as app

try:
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
except Exception:
    pass


def emit(kind, payload=None):
    if kind == "progress":
        print(f"[progress] {payload}", flush=True)


def main():
    paths = [os.path.abspath(p) for p in sys.argv[1:]]
    paths = [p for p in paths if os.path.isfile(p)]
    if not paths:
        print("usage: _live_batch.py file1.sdd [file2.sdd ...]")
        return 1

    app.init_log()
    app.setup_logging_bridge()
    results = []
    try:
        for index, path in enumerate(paths, 1):
            print(f"=== {index}/{len(paths)}: {os.path.basename(path)}",
                  flush=True)
            stats = app.run_pipeline(path, None, emit, delete_dxf=True)
            results.append(stats)
            print(f"    -> {stats['target']}", flush=True)
    except Exception:
        print("ОШИБКА:\n" + traceback.format_exc(), flush=True)
        return 1
    finally:
        if app._OWNED_SCHEMAGEE.get("opened") and app.find_schemagee_window()[0]:
            try:
                with app.stop_suspended():
                    app.close_schemagee(timeout=5.0)
            except Exception:
                pass

    print(f"ИТОГ: обработано {len(results)} из {len(paths)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
