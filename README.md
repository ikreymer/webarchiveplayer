**Please note: this project is no longer being actively developed.**

**Please use the new [Webrecorder Player](http://github.com/webrecorder/webrecorderplayer-electron) app, [available for download here](http://github.com/webrecorder/webrecorderplayer-electron/releases/latest). The Webrecorder Player will receive regular feature updates in sync with https://webrecorder.io/**


# WebArchivePlayer 1.4.7

WebArchivePlayer is a new desktop tool which provides a simple point-and-click wrapper for viewing any web archive file (in [WARC](http://en.wikipedia.org/wiki/Web_ARChive) and ARC format).

To create a web archive (WARC) file of your own, you can use the free https://webrecorder.io/ service to browse any page and then download the recorded WARC file.

The player allows users to pick one or more ARC/WARC from their local machine and browse the contents from any browser. No internet connection is necessary in order to browse the archive.



## Usage (Windows and OS X Apps)

1. Download the latest version:

* **[Download for OS X](https://github.com/ikreymer/webarchiveplayer/raw/master/app/osx/webarchiveplayer.dmg)**

* **[Download for Windows](https://github.com/ikreymer/webarchiveplayer/raw/master/app/windows/webarchiveplayer.exe)**

2. Double click to open. (For OS X, open the .dmg file to mount the volume and extract the player). You may have to agree to allow open files from the internet, and to allow making internet connections (windows only). This still new software and other distribution methods may be added in the future.

3. A file dialog will show up. Browse to an existing WARC or ARC file(s).

   You can use https://webrecorder.io to record pages as you browse and then download the WARC file.

4. A browser will open to [http://localhost:8090/](http://localhost:8090/) listing all the pages in the archive.

5. Click on any page listed to view the replay. Or, enter a url to search the full archive.

6. To exit, simply close the WebArchivePlayer window.

### Example

![OS X Screenshot](/app/osx/osx_screenshot.png?raw=true "Wikipedia Blackout Replay")
![Windows Screenshot](/app/windows/screenshot.png?raw=true "Wikipedia Blackout Replay")

(Replaying screenshot from [Wikipedia SOPA Blackout](https://github.com/ukwa/webarchive-test-suite/tree/master/wikipedia-sopa-blackout-2012). You can [download the WARC](https://github.com/ukwa/webarchive-test-suite/blob/master/wikipedia-sopa-blackout-2012/wikipedia-blackout/sopa-wikipedia-homepage.warc.gz?raw=true) from GitHub.)

## Usage for All Platforms -- Running from python source

Currently, executable versions are available only for OS X and Windows.

However, the player should work on any system that has Python 2.7.x, but requires a little bit more setup.

On other systems (or to build from source):

1. Clone this repo: `git clone https://github.com/ikreymer/webarchiveplayer.git; cd webarchiveplayer`

2. Install by running `python setup.py install` (optionally using a virtualenv)

3. Run `webarchiveplayer [/path/to/warc_or_arc]`


### GUI Mode

If a W/ARC file argument is omitted, the player will attempt to start in GUI mode and show a File Open dialog.

However, in order to run in GUI mode, the wxPython toolkit will also need to be installed seperately.

Refer to instructions at [wxPython Download page](http://wxpython.org/download.php) for your platform.

### wxPython and virtualenv

wxPython does not by default work in virtualenv. The simplest way to make it work is to symlink the system `wxredirect.pth` to the virtualenv site-packages directory. For example, on OS X, if you've installed `virtualenv [myenv]

`ln -s /Library/Python/2.7/site-packages/wxredirect.pth [myenv]/lib/python2.7/site-packages/wxredirect.pth`

### CLI Mode

If a W/ARC file argument is passed to the player, eg:

`webarchiveplayer /path/to/warcfile.warc.gz`

The player will select that file and skip the File Open dialog. Installation of wxPython is not required when specifiyng
the WARC explicitly via command line.

The OS X and Windows applications also support specifying the file via command line.

### Custom Preset Archive Mode

In addition to opening files, WebArchivePlayer can now also be used to provide a point-and-click launcher for
any [pywb](https://github.com/ikreymer/pywb) archive.

If a `config.yaml` file is present in the working directory (same directory as WebArchivePlayer), the specified configuration will be loaded
instead of a file prompt.

This can be used to distribute specific archives together with WebArchivePlayer.

Certain aspects of the player can also be modified in the `config.yaml`, including changing the contents
from 'Web Archive Player' to any custom title and HTML page.


```
webarchiveplayer:
   # initial page to load on start-up
   # eg: http://localhost:8090/my_coll/http://example.com/
   start_url: my_coll/http://example.com/

   # set initial width of player window
   width: 400

   # set initial height of player window
   height: 250

   # set window title
   title: My Archive

   # Load custom contents from local HTML
   desc_html: ./desc.html
   
   # Auto-load WARCs from specified directory (supported from 1.4.6)
   auto_load_dir: ./warcs/
```

For example, one could distribute a WARC together with the player and provide a custom setup.
This includes automatically indexing WARCs on load to allow quick drop in, or configuring a multi-collection archive.

#### Auto-Load WARCs

With version 1.4.6, webarchiveplayer supports indexing WARCs automatically from a designated directory.
Archive files are indexed on each load to allow for dropping or updating the files more easily.

To setup, all that's needed is a `config.yaml` with the following:
   ```
      webarchiveplayer:
          auto_load_dir: ./warcs
          
          title: 'My Archive'
          desc_html: ./desc_page.html
   ```

If WebArchivePlayer is placed in the same directory as the `config.yaml` and `warcs` directory,
the player will automatically load and index all WARC/ARC files found in this directory.

Optionally, the `config.yaml` and `warcs` may also be placed in an `archive` sub-directory.
This allows for an archive to be more easily transported (eg. as a tar-ball or zip file).

The last two params allow for customizing the WebArchivePlayer window.
The `title` param specifies the window title, while the `desc_html` param specifies
the contents of the WebArchivePlayer window.

#### Create multi-collection archive

The following steps describe creating static archive with preset collections
and indexed archive files:

1) Create new directory `my_archive` and switch to it.

2) Copy the WebArchivePlayer application to `my_archive`

2) In `my_archive`, run `wb-manager init my_coll`

3) Run `wb-manager add my_coll <path/to/warc>`

4) Add `config.yaml` in `my_archive`, perhaps with
   ```
      webarchiveplayer:
         start_url: my_coll/http://example.com/
         title: My Archive Demo
   ```

5) Now, when WebArchivePlayer is started in `my_archive`, it will use the WARC in `my_coll` and load `http://localhost:8090/my_coll/http://example.com/` as the starting URL.

6) The `my_archive` dir can be distributed as a standlone archive and player.



### Building GUI Binaries

The binaries can be built by running the builds scripts from the `app` directory:

*Note: wxPython must be installed for this to work. If running in virtualenv, follow instructions above. The install
script will not run if it can't find wxPython*

OS X: (output written to `osx/webarchiveplayer.dmg`)
```
cd app
./build-osx.sh
```

Windows: (output copied to `windows\webarchiveplayer.exe`)
```
cd app
build-windows.bat
```


### Changelist

#### 1.4.7

Ensure config file as desc HTML are read as utf-8

#### 1.4.6

Update to pywb 0.33.1
Support for ``auto_load_dir`` option in ``config.yaml`` (or ``archive/config.yaml``) which specifies a directory
from which to automatically load WARCs on startup.


#### 1.4.5

Update to pywb 0.32.1
Support Webrecorder collection WARCs, read pages/bookmarks from all `warcinfo` records

#### 1.4.1

Update to pywb 0.30.1
Support reading of WARC files with non-HTTP response records (which are skipped).

#### 1.4.0

Build using Python 3 and pywb 0.30.0, using latest pyinstaller
page detect: re-enable reading pagelist from ``json-metadata`` if present in WARC

#### 1.3.0

Support multiple instances by picking a random port if 8090 is not available
Ensure HTML 'resource' records are included in page list
Display error dialog before quitting if unable to read and index WARC/ARCs.
Switch to pywb 0.11.1, many improvements in indexing and replay

#### 1.2.0

Custom preset archive support with custom `config.yaml`
Use HTML for main window rendering
Switch to pywb 0.10.9.1 for more rewriting improvements

#### 1.1.4

Update to pywb 0.10.8, rewriting improvements, add pywb version display

#### 1.1.3

Update to pywb 0.10.6, significant replay improvements

#### 1.1.2
Fix issue where page listing only lists pages for one WARC/ARC when multiple are selected.
Build scripts check for wxPython installation.

#### 1.1.1
Update to use latest pywb release (0.8.3)

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
