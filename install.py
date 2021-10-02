#!/usr/bin/env python3
"""Install my desired packages."""

import json
import pathlib
import re
import shlex
import subprocess

BREW = "/usr/local/bin/brew"
NPM = "/usr/local/bin/npm"


def read_list_from_file(filename: str) -> set:
    """Build a set from a simple multiline text file.

    Args:
        filename: name of the text file

    Returns:
        a set of the unique lines from the file
    """
    filepath = pathlib.Path(filename)
    lines = filepath.read_text().splitlines()
    return set(lines)


def read_formulae() -> set:
    """Obtain Homebrew formulae that are not dependencies of another formula.

    Returns:
        a set of formulae names
    """
    leaves_list = subprocess.check_output([BREW, "leaves"], text=True).splitlines()
    return set(leaves_list)


def read_casks() -> set:
    """Obtain list of casks installed with Homebrew.

    Returns:
        a set of cask names
    """
    cask_list = subprocess.check_output(
        [BREW, "list", "--cask", "-1"], text=True
    ).splitlines()
    return set(cask_list)


def read_taps() -> set:
    """Obtain list of utilized Homebrew taps.

    Returns:
        a set of taps
    """
    tap_list = subprocess.check_output([BREW, "tap"], text=True).splitlines()
    return set(tap_list)


def read_npm() -> set:
    """Obtain list of globally-installed npm packages.

    Returns:
        a set of package names
    """
    pkg_json = subprocess.check_output(
        [NPM, "list", "-g", "--depth", "0", "--json"], text=True
    )
    packages = json.loads(pkg_json)
    return set(packages["dependencies"])


def install_npm_packages() -> None:
    """Install npm packages from text file."""
    to_install = read_list_from_file("npm.txt")
    existing = read_npm()
    cmd = [NPM, "install", "--global"]
    for line in to_install - existing:
        subprocess.check_call(cmd + shlex.split(line))


def install_brew() -> None:
    """Install Homebrew if not installed already."""
    try:
        subprocess.check_output(["/usr/bin/which", "brew"])
    except subprocess.CalledProcessError:
        script = subprocess.check_output(
            [
                "/usr/bin/curl",
                "-fsSL",
                "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh",
            ]
        )
        subprocess.check_call(["/bin/bash", "-c", script])


def install_taps() -> None:
    """Install external Homebrew taps from text file."""
    to_install = read_list_from_file("taps.txt")
    existing = read_taps()
    cmd = [BREW, "tap"]
    for line in to_install - existing:
        subprocess.check_call(cmd + shlex.split(line))


def install_formulae() -> None:
    """Install Homebrew formulae from text file."""
    to_install = read_list_from_file("formulae.txt")
    existing = read_formulae()
    cmd = [BREW, "install"]
    for line in to_install - existing:
        subprocess.check_call(cmd + shlex.split(line))


def install_casks() -> None:
    """Install Homebrew casks from text file and allow through Gatekeeper."""
    to_install = read_list_from_file("casks.txt")
    existing = read_casks()
    cmd = [BREW, "install"]
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


def read_mas() -> set:
    """Read list of App store packages to install.

    Returns:
        set of packages
    """
    sep = re.compile(r"\s{2,}")
    raw_list = subprocess.check_output(["mas", "list"], text=True)
    return {sep.split(i, maxsplit=1)[0] for i in raw_list.splitlines()}


def install_mas() -> None:
    """Install App store packages from text file."""
    app_list = pathlib.Path("mas.json")
    to_install = set(json.loads(app_list.read_text()))
    existing = read_mas()
    for line in to_install - existing:
        subprocess.check_call(["mas", "install", line])


def run() -> None:
    """Run commands in order."""
    install_brew()
    install_taps()
    install_formulae()
    install_casks()
    install_npm_packages()
    install_mas()


if __name__ == "__main__":
    run()
