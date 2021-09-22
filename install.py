#!/usr/bin/env python3

import json
import pathlib
import re
import shlex
import subprocess


def read_list_from_file(filename):
    filepath = pathlib.Path(filename)
    lines = filepath.read_text().splitlines()
    return set(lines)


def read_formulae():
    leaves_list = subprocess.check_output(["brew", "leaves"], text=True).splitlines()
    return set(leaves_list)


def read_casks():
    cask_list = subprocess.check_output(
        ["brew", "list", "--cask", "-1"], text=True
    ).splitlines()
    return set(cask_list)


def read_taps():
    tap_list = subprocess.check_output(["brew", "tap"], text=True).splitlines()
    return set(tap_list)


def read_npm():
    pkg_json = subprocess.check_output(
        ["npm", "list", "-g", "--depth", "0", "--json"], text=True
    )
    packages = json.loads(pkg_json)
    return set(packages["dependencies"])


def install_npm_packages():
    to_install = read_list_from_file("npm.txt")
    existing = read_npm()
    cmd = ["npm", "install", "--global"]
    for line in to_install - existing:
        subprocess.check_call(cmd + shlex.split(line))


def install_brew():
    try:
        subprocess.check_output(["which", "brew"])
    except subprocess.CalledProcessError:
        script = subprocess.check_output(
            [
                "curl",
                "-fsSL",
                "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh",
            ]
        )
        subprocess.check_call(["/bin/bash", "-c", script])


def install_taps():
    to_install = read_list_from_file("taps.txt")
    existing = read_taps()
    cmd = ["brew", "tap"]
    for line in to_install - existing:
        subprocess.check_call(cmd + shlex.split(line))


def install_formulae():
    to_install = read_list_from_file("formulae.txt")
    existing = read_formulae()
    cmd = ["brew", "install"]
    for line in to_install - existing:
        subprocess.check_call(cmd + shlex.split(line))


def install_casks():
    to_install = read_list_from_file("casks.txt")
    existing = read_casks()
    cmd = ["brew", "install"]
    app_pattern = re.compile("'/Applications/[^']+'")
    for line in to_install - existing:
        print(f"Installing {line}")
        result = subprocess.check_output(cmd + shlex.split(line), text=True)
        print(result)
        app_path = app_pattern.search(result)
        if app_path:
            app_pathname = app_path.group().strip("'")
            subprocess.check_call(
                ["sudo", "spctl", "--add", "--label", '"homebrew"', app_pathname]
            )
            subprocess.check_call(
                ["sudo", "xattr", "-d", "com.apple.quarantine", app_pathname]
            )


def read_mas():
    sep = re.compile("\s{2,}")
    raw_list = subprocess.check_output(["mas", "list"], text=True)
    # apps = {k:v for k,v in (i.split()[0:2] for i in raw_list.splitlines())}
    return set(sep.split(i, maxsplit=1)[0] for i in raw_list.splitlines())


def install_mas():
    app_list = pathlib.Path("mas.json")
    to_install = set(json.loads(app_list.read_text()))
    existing = read_mas()
    for line in to_install - existing:
        subprocess.check_call(["mas", "install", line])


def run():
    install_brew()
    install_taps()
    install_formulae()
    install_casks()
    install_npm_packages()
    install_mas()


if __name__ == "__main__":
    run()
