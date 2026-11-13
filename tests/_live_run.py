# -*- coding: utf-8 -*-
"""Живой прогон указанного .sdd через Schemagee (без GUI).

Использование:
    python tests\\_live_run.py "D:\\ToDWG\\Примеры\\file.sdd" [--sheets N]

Без --sheets число листов определяется автоматически (диалог печати).
Во время работы нельзя трогать мышь и клавиатуру.
"""
import argparse
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ToDWG_v2 as app

try:                        # консоль Windows может быть в cp1251
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
except Exception:
    pass


def emit(kind, payload=None):
    if payload is None:
        print(f"[{kind}]", flush=True)
    else:
        print(f"[{kind}] {payload}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Живой прогон одного .sdd")
    parser.add_argument("sdd", help="путь к файлу .sdd")
    parser.add_argument("--sheets", type=int, default=None,
                        help="число листов (по умолчанию — авто)")
    parser.add_argument("--format", default="A2",
                        choices=["A2", "A3", "A4"],
                        help="формат листа альбома")
    parser.add_argument("--orient", default="landscape",
                        choices=["landscape", "portrait"],
                        help="ориентация листа")
    opts = parser.parse_args()

    if not os.path.isfile(opts.sdd):
        print("нет файла:", opts.sdd)
        return 1

    paper_w, paper_h = app.paper_size(opts.format, opts.orient == "landscape")
    app.init_log()
    app.setup_logging_bridge()
    print(f"START {opts.sdd} sheets={opts.sheets} "
          f"paper={opts.format} {opts.orient}", flush=True)
    try:
        app.run_pipeline(opts.sdd, opts.sheets, emit,
                         paper_w=paper_w, paper_h=paper_h)
    except Exception:
        print("ОШИБКА:\n" + traceback.format_exc(), flush=True)
        return 1
    finally:
        # Если сбой случился до штатного закрытия, Schemagee остаётся
        # открытым и блокирует следующий запуск — закрываем его здесь.
        if app._OWNED_SCHEMAGEE.get("opened") and app.find_schemagee_window()[0]:
            try:
                with app.stop_suspended():
                    app.close_schemagee(timeout=5.0)
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
