#!/usr/bin/env python3

import pathlib
import subprocess


def read_list_from_file(filename):
    filepath = pathlib.Path(filename)
    lines = filepath.read_text().strip().split('\n')
    return set(lines)


def read_formulae():
    leaves_list = subprocess.check_output(['brew','leaves'],text=True).strip().split('\n')
    return set(leaves_list)


def read_casks():
    cask_list = subprocess.check_output(['brew', 'list', '--cask', '-1'],text=True).strip().split('\n')
    return set(cask_list)


def read_taps():
    tap_list = subprocess.check_output(['brew', 'tap'],text=True).strip().split('\n')
    return set(tap_list)


def install_brew():
    try:
        subprocess.check_output(['which', 'brew'])
    except subprocess.CalledProcessError:
        script = subprocess.check_output(['curl', '-fsSL', 'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh'])
        subprocess.check_call(['/bin/bash', '-c', script])


def install_taps():
    taps_to_install = read_list_from_file('taps.txt')
    taps = read_taps()
    for tap in taps_to_install - taps:
        subprocess.check_call(['brew', 'tap', tap])


def install_formulae():
    formulae_to_install = read_list_from_file('formulae.txt')
    formulae = read_formulae()
    for formula in formulae_to_install - formulae:
        subprocess.check_call(['brew', 'install', formula])
        

def install_casks():
    casks_to_install = read_list_from_file('casks.txt')
    casks = read_casks()
    for cask in casks_to_install - casks:
        subprocess.check_call(['brew', 'install', cask])


def run():
    install_brew()
    install_taps()
    install_formulae()
    install_casks()

if __name__ == "__main__":
    run()
