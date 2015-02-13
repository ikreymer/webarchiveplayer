#!/bin/bash
pip install pyinstaller
pyinstaller --clean -y -F -w webarchiveplayer.py

mkdir osx
rm osx/webarchiveplayer.dmg

hdiutil create -volname WebArchivePlayer -srcfolder ./dist/webarchiveplayer.app -ov -format UDZO ./osx/webarchiveplayer.dmg
