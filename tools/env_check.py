#!/usr/bin/env python
"""环境体检：一条命令确认 Python 版本 / 虚拟环境 / 项目配置是否就位。

用法（在项目根目录 D:\\ai-learning 下）：
    python tools\\env_check.py

退出码：0 = 全部通过；1 = 有未通过项。
"""
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []


def add(name, ok, detail, skip=False):
    rows.append((name, ok, detail, skip))


def check_python_version():
    major, minor = sys.version_info[:2]
    add("Python 主次版本是 3.12", (major, minor) == (3, 12),
        "%d.%d.%d" % (major, minor, sys.version_info[2]))


def check_in_venv():
    ok = sys.prefix != sys.base_prefix
    add("确实运行在虚拟环境里", ok, "prefix=%s" % sys.prefix)


def check_executable():
    exe = sys.executable.replace("/", "\\")
    ok = "\\.venv\\" in exe.lower()
    add("解释器在项目 .venv 内", ok, exe)


def check_pin_file():
    path = os.path.join(ROOT, ".python-version")
    if not os.path.exists(path):
        add(".python-version 指向 3.12", False, "文件不存在，先运行 uv python pin 3.12")
        return
    with open(path, encoding="utf-8") as f:
        val = f.read().strip()
    add(".python-version 指向 3.12", val.startswith("3.12"), val)


def check_requires_python():
    path = os.path.join(ROOT, "pyproject.toml")
    if not os.path.exists(path):
        add("pyproject.toml 的 requires-python", True,
            "尚未创建（首次 uv add 时生成），暂不判定", skip=True)
        return
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r'requires-python\s*=\s*"([^"]+)"', txt)
    if not m:
        add("pyproject.toml 的 requires-python", False, "文件里找不到 requires-python")
        return
    spec = m.group(1)
    too_high = re.search(r">=\s*3\.(1[3-9])", spec)
    add("requires-python 允许 3.12", not too_high, spec)


def check_encoding():
    enc = sys.getdefaultencoding()
    fs = sys.getfilesystemencoding()
    add("默认编码可用（utf-8 系）", enc.lower().startswith("utf"),
        "default=%s, filesystem=%s" % (enc, fs))


def main():
    check_python_version()
    check_in_venv()
    check_executable()
    check_pin_file()
    check_requires_python()
    check_encoding()

    print("=" * 62)
    print(" 环境体检  项目根：%s" % ROOT)
    print("=" * 62)
    fails = 0
    for i, (name, ok, detail, skip) in enumerate(rows, 1):
        if skip:
            tag = "[SKIP]"
        elif ok:
            tag = "[PASS]"
        else:
            tag = "[FAIL]"
            fails += 1
        print("%s %d. %-26s  %s" % (tag, i, name, detail))
    print("-" * 62)
    total = sum(1 for r in rows if not r[3])
    print(" 通过 %d/%d 项，未通过 %d 项" % (total - fails, total, fails))
    if fails:
        print(" 详见上方 [FAIL] 行；改完重新运行本脚本。")
    else:
        print(" 环境就绪。")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
