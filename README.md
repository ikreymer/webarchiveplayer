# WebArchivePlayer 1.1.0

WebArchivePlayer is a new desktop tool which provides a simple point-and-click wrapper for viewing any web archive file (in [WARC](http://en.wikipedia.org/wiki/Web_ARChive) and ARC format). These files are international standard formats used by web archiving institutions, including Internet Archive's Wayback Machine and newer projects such as https://webrecorder.io

The player allows users to pick one or more ARC/WARC from their local machine and browse the contents from any browser. No internet connection is necessary in order to browse the archive.


## Usage (Windows and OS X Apps)

1. Download the latest version:

* **[Download for OS X](https://github.com/ikreymer/webarchiveplayer/raw/master/app/osx/webarchiveplayer.dmg)**

* **[Download for Windows](https://github.com/ikreymer/webarchiveplayer/raw/master/app/windows/webarchiveplayer.exe)**

2. Double click to open. (For OS X, open the .dmg file to mount the volume and extract the player). You may have to agree to allow open files from the internet, and to allow making internet connections (windows only). This still new software and other distribution methods may be added in the future.

3. A file dialog will show up. Browse to an existing WARC or ARC file(s).

   You can use https://webrecorder.io to record pages as you browse and then download the WARC file.

4. A browser will open to [http://localhost:8090/replay/](http://localhost:8090/replay/) listing all the pages in the archive.

5. Click on any page listed to view the replay. Or, enter a url to search the full archive.

6. To exit, simply close the WebArchivePlayer window.

### Example

![OS X Screenshot](/app/osx/osx_screenshot.png?raw=true "Wikipedia Blackout Replay")
![Windows Screenshot](/app/windows/screenshot.png?raw=true "Wikipedia Blackout Replay")

(Replaying screenshot from [Wikipedia SOPA Blackout](https://github.com/ukwa/webarchive-test-suite/tree/master/wikipedia-sopa-blackout-2012). You can [download the WARC](https://github.com/ukwa/webarchive-test-suite/blob/master/wikipedia-sopa-blackout-2012/wikipedia-blackout/sopa-wikipedia-homepage.warc.gz?raw=true) from GitHub.)

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

### Changelist

#### 1.1.0
Support opening multiple WARC/ARC files at once. Also fix issue with opening files with spaces in filename.

#### 1.0.1
Initial release.


## How it Works

WebArchivePlayer is a simple wrapper over the [pywb web archiving tools](https://github.com/ikreymer/pywb) using
[pyinstaller](http://www.pyinstaller.org/) to create a standalone, GUI wrapper. The [wxPython](http://wxpython.org/) toolkit is used to provide the GUI.
The wrapper starts a local server which serves content from the selected web archive, using pywb to handle the rest.

Consult the pywb documentation for more info on web archive replay.

### Questions / Issues

Please feel free to open an issue on this page for any problems / questions / concerns regarding this tool. This is a brand new software, so feedback is encouraged.

### Other Tools

Another project, which in part inspired WebArchivePlayer, is Mat Kelly's excellent [WAIL](http://matkelly.com/wail/) project, which provides a GUI for different web crawling and replay systems.
