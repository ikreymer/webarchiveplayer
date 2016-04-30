#!/bin/bash
python -c "import wx; print(wx.__file__)" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "wxPython is not installed. Can't build GUI binary"
    if [ -n $VIRTUAL_ENV ]; then
        echo "Appear to be running in a virtualenv. You may need to symlink:"
        echo "ln -s [system python path]/site-packages/wxredirect.pth $VIRTUAL_ENV/lib/python2.7/site-packages/wxredirect.pth"
    fi
    exit 1
fi


pip install pyinstaller
pyinstaller --clean -y -F -w webarchiveplayer.py

# set the version in Info.plist manually
version=$(python -c 'import archiveplayer.version; print(archiveplayer.version.__version__)')
sed -i'' -e "s/0.0.0/$version/g" ./dist/webarchiveplayer.app/Contents/Info.plist

mkdir osx
rm osx/webarchiveplayer.dmg

hdiutil create -volname WebArchivePlayer -srcfolder ./dist/webarchiveplayer.app -ov -format UDZO ./osx/webarchiveplayer.dmg
