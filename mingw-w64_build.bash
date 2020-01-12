#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

pacman -Syu
pacman -S --needed mingw-w64-x86_64-python-pillow mingw-w64-x86_64-python-pyqt5 mingw-w64-x86_64-python-pip
pip install pyinstaller

pyinstaller --noconsole $DIR/risovaka.py
cp -r $DIR/gui $DIR/europe.png $DIR/europe.json $DIR/dist/risovaka
