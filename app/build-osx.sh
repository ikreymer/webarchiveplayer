#!/bin/bash
pyinstaller -F -w webarchiveplayer.py
hdiutil create -volname WebArchivePlayer -srcfolder ./dist/webarchiveplayer.app -ov -format UDZO ./osx/webarchiveplayer.dmg
