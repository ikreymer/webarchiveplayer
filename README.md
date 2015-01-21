# WebArchivePlayer (Alpha)

WebArchivePlayer is a brand new desktop tool which provides a point-and-click wrapper for viewing web archive files (WARC and ARC).
The player allows users to browse web archive files, such as those created via https://webrecorder.io locally on their desktop.
Once downloaded, no internet connection is necessary in order to browse the archive.

## Usage (Windows and OS X Apps)

1. Download the latest version:

* **[Download for OS X](https://github.com/ikreymer/webarchiveplayer/raw/master/app/osx/webarchiveplayer.dmg)**

* **[Download for Windows](https://github.com/ikreymer/webarchiveplayer/raw/master/app/windows/webarchiveplayer.exe)**

2. Double click to open. (For OS X, open the .dmg file to mount the volume and extract the player). You may have to agree to open files from the internet. (This is still currently new experimental software).

3. A file dialog will show up. Browse to an existing WARC or ARC file(s).

   You can use https://webrecorder.io to record pages as you browse and then download the WARC file.

4. A browser will open to [http://localhost:8090/replay/](http://localhost:8090/replay/) listing all the pages in the archive.

5. Click on any page listed to view the replay. Or, enter a url to search the full archive.

6. To exit, simply close the WebArchivePlayer window.


## Usage for All Platforms -- Running from python source

Currently, executable versions are available only for OS X and Windows.

However, the player should work on any system that has Python 2.7, but requires a little bit more setup.

On other systems (or to build from source):

1. Clone this repo: `git clone https://github.com/ikreymer/webarchiveplayer.git; cd webarchiveplayer`

2. Run `webarchiveplayer [/path/to/warc_or_arc]`


### GUI Mode

If a W/ARC file argument is omitted, the player will attempt to start in GUI mode and show a File Open dialog.

However, in order to run in GUI mode, the wxPython toolkit will also need to be installed seperately.

Refer to instructions at [wxPython Download page](http://wxpython.org/download.php) for your platform.

### CLI Mode

If a W/ARC file argument is passed to the player, eg:

`webarchiveplayer /path/to/warcfile.warc.gz`

The player will select that file and skip the File Open dialog. Installtion of wxPython is not required when specifiyng
the WARC explicitly via command line.

The OS X and Windows applications also support specifying the file via command line.

## How it Works

WebArchivePlayer is a simple wrapper over the [pywb web archiving tools](https://github.com/ikreymer/pywb) using
[pyinstaller](http://www.pyinstaller.org/) to create a standalone, GUI wrapper. The [wxPython](http://wxpython.org/) toolkit is used to provide the GUI.
The wrapper starts a local server which serves content from the selected web archive, using pywb to handle the rest.

Consult the pywb documentation for more info on web archive replay.

### Similar Tools

Another project, which in part inspired WebArchivePlayer, is Mat Kelly's excellent [WAIL](http://matkelly.com/wail/) project, which provides a GUI for different crawling and replay systems.
