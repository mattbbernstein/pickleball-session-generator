#!/usr/bin/env python3
"""Build a standalone pickleball-session-generator executable with PyInstaller.

Usage:
    python build.py

Run from an activated venv that has pyinstaller installed
(pip install -r requirements-dev.txt).
"""
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ENTRY_POINT = PROJECT_ROOT / "src" / "best_session.py"
APP_NAME = "pickleball-session-generator"
BUILD_DIRS = ["build", "dist", "__pycache__"]


def check_pyinstaller():
    if shutil.which("pyinstaller") is None:
        sys.exit(
            "pyinstaller not found.\n"
            "Install build dependencies first:\n"
            "    pip install -r requirements-dev.txt"
        )


def clean():
    for name in BUILD_DIRS:
        path = PROJECT_ROOT / name
        if path.exists():
            shutil.rmtree(path)
    spec_file = PROJECT_ROOT / f"{APP_NAME}.spec"
    if spec_file.exists():
        spec_file.unlink()


def build():
    subprocess.run(
        [
            "pyinstaller",
            "--onefile",
            "--name", APP_NAME,
            str(ENTRY_POINT),
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )


def main():
    check_pyinstaller()
    clean()
    build()

    exe_name = f"{APP_NAME}.exe" if platform.system() == "Windows" else APP_NAME
    exe_path = PROJECT_ROOT / "dist" / exe_name

    print()
    if exe_path.exists():
        print(f"Build complete: {exe_path}")
    else:
        sys.exit(f"Build finished but expected output not found: {exe_path}")


if __name__ == "__main__":
    main()
