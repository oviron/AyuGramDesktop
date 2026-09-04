import json
import re
import shlex
import sys
from pathlib import Path


def check(build):
    cache = (build / "CMakeCache.txt").read_text()
    for setting in (
        "CMAKE_BUILD_TYPE:STRING=Release",
        "CMAKE_OSX_ARCHITECTURES:STRING=arm64",
        "DESKTOP_APP_DISABLE_AUTOUPDATE:BOOL=ON",
    ):
        if setting not in cache:
            raise ValueError(f"Неверная настройка сборки: {setting}")
    commands = json.loads((build / "compile_commands.json").read_text())
    product = [
        entry for entry in commands
        if "/Telegram/SourceFiles/" in entry["file"]
    ]
    if not product:
        raise ValueError("Нет команд компиляции приложения")
    for entry in product:
        args = entry.get("arguments") or shlex.split(entry["command"])
        optimization = [arg for arg in args if re.fullmatch(r"-O[0-3szg]", arg)]
        if not optimization or optimization[-1] not in ("-O2", "-O3", "-Os", "-Oz"):
            raise ValueError(f"Нет оптимизации: {entry['file']}")
        if "-D_DEBUG" in args or "-DNDEBUG" not in args:
            raise ValueError(f"Отладочная конфигурация: {entry['file']}")
        if "-arch" not in args or args[args.index("-arch") + 1] != "arm64":
            raise ValueError(f"Неверная архитектура: {entry['file']}")
    ninja = (build / "build.ninja").read_text()
    if re.search(r"libQt6\w+_debug\.a", ninja):
        raise ValueError("В Release подключён отладочный Qt")
    print(f"Release arm64: проверено {len(product)} команд компиляции")


if __name__ == "__main__":
    check(Path(sys.argv[1]))
