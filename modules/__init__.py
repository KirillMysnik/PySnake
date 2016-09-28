from importlib import import_module
import os
import sys

from __main__ import get_resource


def parse_packages(dir_):
    packages = []
    for name in os.listdir(get_resource(dir_)):
        if name.startswith('__') and name.endswith('__'):
            continue

        if os.path.isdir(get_resource(os.path.join(dir_, name))):
            packages.append(name)

    return packages


def parse_modules(dir_):
    modules = []
    for name in os.listdir(get_resource(dir_)):
        if not name.endswith('.py'):
            continue

        if name.startswith('__') and name.endswith('__.py'):
            continue

        if os.path.isfile(get_resource(os.path.join(dir_, name))):
            modules.append(os.path.splitext(name)[0])

    return modules


current_dir = os.path.dirname(__file__)

if hasattr(sys, "_MEIPASS"):
    print("PyInstaller detected! Using pre-built list of modules.")
    __all__ = []
    with open(get_resource(os.path.join("resource", "modules.txt"))) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            __all__.append(line)
else:
    print("Scanning modules...")
    __all__ = parse_packages(current_dir) + parse_modules(current_dir)


for module in __all__:
    module = "modules.{}".format(module)
    print("loading {}...".format(module))
    import_module(module)
