# -*- coding: utf-8 -*-
"""Создаёт GitHub Release для jckeil/ToDWG и прикладывает собранный exe.

Токен берётся из GH_TOKEN или из сохранённых учётных данных git;
тело релиза — из CHANGELOG.md.

Использование:
    python tests\\_make_release.py v1.6 [путь\\к\\ToDWG_v1.6.exe]
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO = "jckeil/ToDWG2"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")


def default_asset(version):
    """Путь к exe версии: dist\\ToDWG_v1.6.exe."""
    return os.path.join(ROOT, "dist", f"ToDWG_{version}.exe")


def token_from_git():
    """Токен из сохранённых учётных данных git (ничего не пишется на диск)."""
    try:
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0",
                   GCM_INTERACTIVE="never")
        result = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True, text=True, timeout=25, cwd=ROOT, env=env)
        for line in result.stdout.splitlines():
            if line.startswith("password="):
                return line[len("password="):].strip()
    except Exception as e:
        print(f"git credential: {e}")
    return ""


TOKEN = os.environ.get("GH_TOKEN") or token_from_git()


def api(method, url, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", f"token {TOKEN}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("Content-Type", "application/json; charset=utf-8")
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def upload_asset(upload_url, path):
    """Загружает файл в ассеты релиза (имя — имя файла)."""
    name = os.path.basename(path)
    url = upload_url.split("{")[0] + f"?name={urllib.parse.quote(name)}"
    with open(path, "rb") as fp:
        data = fp.read()
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Authorization", f"token {TOKEN}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("Content-Type", "application/octet-stream")
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.loads(response.read().decode("utf-8"))


def section(text, version):
    base = version.split("-")[0]
    pattern = rf"^## {re.escape(base)}.*?$(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.S | re.M)
    return match.group(1).strip() if match else ""


def main():
    if not TOKEN:
        print("нет GH_TOKEN")
        return 1
    version = sys.argv[1] if len(sys.argv) > 1 else "v1.6"
    asset = sys.argv[2] if len(sys.argv) > 2 else default_asset(version)

    text = open(CHANGELOG, encoding="utf-8").read()
    tags = [t["name"] for t in api(
        "GET", f"https://api.github.com/repos/{REPO}/tags")]
    print("теги на GitHub:", ", ".join(tags) or "нет")

    if version not in tags:
        print(f"{version}: нет тега на GitHub — пропуск")
        return 1

    releases = api("GET", f"https://api.github.com/repos/{REPO}/releases")
    existing = [r for r in releases if r.get("tag_name") == version]
    if existing:
        release = existing[0]
        print(f"{version}: релиз уже есть — {release.get('html_url')}")
    else:
        body = section(text, version)
        if not body:
            print(f"{version}: пустая секция в CHANGELOG — пропуск")
            return 1
        payload = {
            "tag_name": version,
            "name": f"ToDWG {version}",
            "body": body,
            "draft": False,
            "prerelease": True,
        }
        try:
            release = api(
                "POST", f"https://api.github.com/repos/{REPO}/releases",
                payload)
            print(f"{version}: релиз создан — {release.get('html_url')}")
        except urllib.error.HTTPError as e:
            print(f"{version}: ошибка {e.code}: "
                  f"{e.read().decode('utf-8', 'replace')[:300]}")
            return 1

    if asset and os.path.isfile(asset):
        have = {a.get("name") for a in release.get("assets", [])}
        if os.path.basename(asset) in have:
            print(f"  {os.path.basename(asset)}: уже загружен")
        else:
            try:
                uploaded = upload_asset(release["upload_url"], asset)
                print(f"  загружено: {uploaded.get('name')} "
                      f"({uploaded.get('size')} байт)")
            except urllib.error.HTTPError as e:
                print(f"  ошибка загрузки {e.code}: "
                      f"{e.read().decode('utf-8', 'replace')[:300]}")
    else:
        print("  exe не найден — релиз без файла")
    return 0


if __name__ == "__main__":
    sys.exit(main())
