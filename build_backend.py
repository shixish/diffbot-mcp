"""setuptools backend that also exposes the Glama virtualenv to python3.

Glama runs `uv sync`, which installs into /app/.venv, then starts
`python3 diffbot_mcp_server.py`. That python3 is the uv-managed base
interpreter, so the import of fastmcp fails. uv refuses a normal install
into it. When this build runs as root with that venv already created,
write a .pth file into the base interpreter so python3 searches the venv.
"""

import os
from pathlib import Path

import setuptools.build_meta as setuptools_backend
from setuptools.build_meta import *  # noqa: F403

VENV = Path("/app/.venv")
PTH_NAME = "diffbot-venv.pth"


def expose_venv_to_base_python() -> None:
    if getattr(os, "geteuid", lambda: 1)() != 0:
        return
    config = VENV / "pyvenv.cfg"
    if not config.is_file():
        return
    values = {}
    for line in config.read_text().splitlines():
        if " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        values[key] = value.strip()
    home = values.get("home")
    version = values.get("version_info")
    if not home or not version:
        return
    pyver = "python" + ".".join(version.split(".")[:2])
    venv_site = VENV / "lib" / pyver / "site-packages"
    if not venv_site.is_dir():
        return
    prefix = Path(home).resolve().parent
    if "uv/python" not in prefix.as_posix():
        return
    try:
        for base_site in prefix.glob(f"lib/{pyver}/site-packages"):
            base_site.mkdir(parents=True, exist_ok=True)
            (base_site / PTH_NAME).write_text(f"{venv_site}\n")
    except OSError:
        return


def build_wheel(*args, **kwargs):
    wheel = setuptools_backend.build_wheel(*args, **kwargs)
    expose_venv_to_base_python()
    return wheel


def build_editable(*args, **kwargs):
    wheel = setuptools_backend.build_editable(*args, **kwargs)
    expose_venv_to_base_python()
    return wheel
