from pywb.framework.wsgi_wrappers import init_app # start_wsgi_server
from pywb.webapp.pywb_init import create_wb_router

from pywb.warc.cdxindexer import write_multi_cdx_index

from pywb.webapp.handlers import WBHandler

from pywb import __version__ as pywb_version

from pagedetect import PageDetectSortedWriter
from version import __version__, INFO_URL

import os
import shutil
import sys
import yaml
import tempfile

from multiprocessing import Process
from threading import Thread

from datetime import datetime

from pywb.warc import cdxindexer
from argparse import ArgumentParser

import webbrowser
import atexit

no_wx = False
try:
    import wx
    import wx.html
    wxFrame = wx.Frame
except:
    no_wx = True
    wxFrame = object

import waitress.server
import socket


#=================================================================
PORT = 8090
PLAYER_URL = 'http://localhost:{0}/'

PYWB_URL = 'https://github.com/ikreymer/pywb'


#=================================================================
class ArchivePlayer(object):
    CDX_NAME = 'index.cdx'

    DEFAULT_CONFIG_FILE = """
collections:
    '{coll_name}':
        index_paths: {index_paths}

        wb_handler_class: !!python/name:archiveplayer.archiveplayer.ReplayHandler

archive_paths: {archive_path}

search_html: pagelist_search.html

framed_replay: inverse

enable_auto_colls: false

enable_memento: true

enable_cdx_api: true

template_packages:
    - pywb
    - archiveplayer

"""

    def __init__(self, archivefiles):
        self.archivefiles = archivefiles

        self.coll_name = ''

        self.cdx_file = tempfile.NamedTemporaryFile(delete=False,
                                                    suffix='.cdxj',
                                                    prefix='cdx')

        self.path_index = tempfile.NamedTemporaryFile(delete=False,
                                                      suffix='.txt')

        try:
            pagelist = self.update_cdx(self.cdx_file, archivefiles)
        except Exception as e:
            msg = "WebArchivePlayer is unable to read the input file(s) and will quit.\n\nDetails: " + str(e)[:255]
            if no_wx:
                sys.stderr.write(msg + '\n')
            else:
                dlg = wx.MessageDialog(None, msg, "Error Reading Web Archive File(s)", style=wx.OK)
                dlg.ShowModal()
            sys.exit(1)

        config = self._load_dynamic_config()
        config['_pagelist'] = pagelist

        config['_archivefiles'] = archivefiles
        self.write_path_index()
        self.application = init_app(create_wb_router,
                                    load_yaml=False,
                                    config=config)

    def close(self):
        if self.cdx_file:
            try:
                os.remove(self.cdx_file.name)
            except:
                pass
            self.cdx_file = None

        if self.path_index:
            try:
                os.remove(self.path_index.name)
            except:
                pass
            self.path_index = None

    def write_path_index(self):
        path_index_lines = [os.path.basename(f) + '\t' + f
                            for f in self.archivefiles]

        path_index_lines = sorted(path_index_lines)
        self.path_index.write('\n'.join(path_index_lines))
        self.path_index.flush()

    def _load_dynamic_config(self):
        def format_func(contents):
            archive_path = self.path_index.name

            contents = contents.format(index_paths=self.cdx_file.name,
                                       archive_path=archive_path,
                                       coll_name=self.coll_name)

            return contents


        return load_config(default_config=self.DEFAULT_CONFIG_FILE,
                           format_func=format_func)



    def update_cdx(self, output_cdx, inputs):
        """
        Output sorted, post-query resolving cdx from 'input_' warc(s)
        to 'output_cdx'. Write cdx to temp and rename to output_cdx
        when completed to ensure atomic updates of the cdx.
        """

        writer_cls = PageDetectSortedWriter
        options = dict(sort=True,
                       surt_ordered=True,
                       append_post=True,
                       cdxj=True,
                       include_all=True,
                       writer_add_mixin=True)

        options['writer_cls'] = writer_cls

        writer = write_multi_cdx_index(output_cdx.name, inputs, **options)

        return writer.pages

    @staticmethod
    def timestamp20():
        """
        Create 20-digit timestamp, useful to timestamping temp files
        """
        now = datetime.utcnow()
        return now.strftime('%Y%m%d%H%M%S%f')


#=================================================================
class StaticPywbApp(object):
    def __init__(self, static_config):
        self.application = init_app(create_wb_router,
                                    load_yaml=False,
                                    config=static_config)
    def close(self):
        pass


#=================================================================
class ReplayHandler(WBHandler):
    def __init__(self, query_handler, config=None):
        super(ReplayHandler, self).__init__(query_handler, config)
        self.pagelist = config.get('_pagelist', [])
        self.archivefiles = config.get('_archivefiles', '')

    def render_search_page(self, wbrequest, **kwargs):
        kwargs['pagelist'] = self.pagelist
        kwargs['archivefile'] = ', '.join(self.archivefiles)
        kwargs['version'] = __version__
        kwargs['pywb_version'] = pywb_version
        return super(ReplayHandler, self).render_search_page(wbrequest, **kwargs)



DEFAULT_HTML_PAGE = """
<!DOCTYPE html>
<html>
<body>
<h1>Web Archive Player {version}</h1>
<h3>(pywb {pywb_version})</h3>

<p>Archive Player Server running at:<br/>
<a href="{player_url}">{player_url}</a>
</p>

<p>For more info about Web Archive Player, please visit:<br/>
<a href="{info_url}">{info_url}</a>
</p>

</body>
</html>
"""

#=================================================================
class TopFrame(wxFrame):
    def init_controls(self, contents=None, title=None, player_url=PLAYER_URL):
        self.menu_bar  = wx.MenuBar()
        self.help_menu = wx.Menu()

        self.help_menu.Append(wx.ID_EXIT,   "&QUIT")

        if wx.Platform != "__WXMAC__":
            self.menu_bar.Append(self.help_menu, "File")

        self.Bind(wx.EVT_MENU, self.quit, id=wx.ID_EXIT)
        self.SetMenuBar(self.menu_bar)

        self.html = wx.html.HtmlWindow(self)
        self.html.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.on_load_url)

        if not title:
            title = 'Web Archive Player ' + __version__

        self.SetTitle(title)

        if not contents:
            contents = DEFAULT_HTML_PAGE

        contents = contents.format(version=__version__,
                                   pywb_version=pywb_version,
                                   player_url=player_url,
                                   info_url=INFO_URL)

        self.html.SetPage(contents)

        # set later
        self.archiveplayer = None

    def on_load_url(self, evt):
        info = evt.GetLinkInfo()
        href = info.GetHref()
        #wx.LaunchDefaultBrowser(href)
        webbrowser.open(href)

    def quit(self, cmd):
        self.Close()
        if self.archiveplayer:
            self.archiveplayer.close()

    def select_file(self):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
        #dialog = wx.DirDialog(top, 'Please select a directory containing archive files (WARC or ARC)', style=style)
        dialog = wx.FileDialog(parent=self,
                               message='Please select a web archive (WARC or ARC) file',
                               wildcard='WARC or ARC (*.gz; *.warc; *.arc)|*.gz;*.warc;*.arc',
                               #wildcard='WARC or ARC (*.gz; *.warc; *.arc)|*.gz; *.warc; *.arc',
                               style=style)

        if dialog.ShowModal() == wx.ID_OK:
            paths = dialog.GetPaths()
        else:
            paths = None

        dialog.Destroy()
        return paths


#=================================================================
class WaitressServer(object):
    def __init__(self, app):
        port = PORT
        if port != 0 and not self.is_open(port):
            port = 0

        self.server = self._do_create(app, port)
        self.port = self.server.socket.getsockname()[1]

    def is_open(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.bind(('0.0.0.0', port))
            sock.close()
            is_open = True
        except Exception as e:
            is_open = False

        return is_open

    def _do_create(self, app, port):
        return waitress.server.create_server(app, port=port, threads=10)

    def __call__(self):
        self.server.run()


#=================================================================
def ensure_close(archiveplayer):
    print('Deleting Temps')
    if archiveplayer:
        archiveplayer.close()


#=================================================================
def load_config(default_config=None, format_func=None):
    if os.path.isdir('archive'):
        os.chdir('archive')

    config_file = os.environ.get('PYWB_CONFIG_FILE', 'config.yaml')
    try:
        with open(config_file) as fh:
            contents = fh.read()
    except:
        contents = default_config

    if not contents:
        return {}

    print('pywb config')
    print('===========')

    if format_func:
        contents = format_func(contents)

    config = yaml.load(contents)

    return config


#=================================================================
def main():
    global PORT

    parser = ArgumentParser('Web Archive Player')
    parser.add_argument('archivefiles', nargs='*')
    parser.add_argument('--port', nargs='?', default=PORT, type=int)
    parser.add_argument('-v', '--version', action='store_true')
    parser.add_argument('--headless', action='store_true',
                        help="Run without a GUI (defaults to true if wxPython not installed)")

    r = parser.parse_args()

    if r.version:
        print(__version__)
        sys.exit(0)

    PORT = r.port

    global PLAYER_URL_TEMP
    frame = None

    global no_wx
    if r.headless:
        no_wx = True

    if not no_wx:
        app = wx.App()

        static_config = load_config()

        player_config = static_config.get('webarchiveplayer', {})
        size = (int(player_config.get('width', 400)), int(player_config.get('height', 200)))

        frame = TopFrame(None, size=size)

        contents = None
        title = player_config.get('title')
        desc_html_file = player_config.get('desc_html')

        if desc_html_file:
            try:
                with open(desc_html_file) as fh:
                    contents = fh.read()
            except:
                contents = None

    else:
        static_config = load_config()


    # ignore this and continue loading with warcs specified by user
    if static_config:
        if static_config.get('webarchiveplayer', {}).get('select_user_warcs', False):
            static_config = None

    if static_config:
        archiveplayer = StaticPywbApp(static_config)
        start_url = static_config.get('webarchiveplayer', {}).get('start_url', '')
        if start_url == 'none':
            start_url = None
        else:
            start_url = PLAYER_URL + start_url

    else:
        if r.archivefiles:
            filenames = r.archivefiles
        else:
            if no_wx:
                print('Sorry, the wxPython toolkit must be installed to run in GUI mode')
                print('See http://wxpython.org/download.php for installation info')
                print('')
                print('You can still start webarchiveplayer directly by specifying a W/ARC file via the command line:')
                print(sys.argv[0] + ' <path to WARC>')
                return

            filenames = frame.select_file()
            if filenames:
                filenames = map(lambda x: x.encode('utf-8'), filenames)

        if not filenames:
            return

        archiveplayer = ArchivePlayer(filenames)
        atexit.register(ensure_close, archiveplayer)

        start_url = PLAYER_URL

    # Create Server
    server = WaitressServer(archiveplayer.application)
    start_url = start_url.format(server.port)

    if frame:
        frame.init_controls(contents, title, start_url)
        frame.archiveplayer = archiveplayer

        server_thread = Thread(target=server)
        server_thread.daemon = True
        server_thread.start()

        if start_url:
            webbrowser.open(start_url)

        frame.Show()
        app.MainLoop()
    else:
        if start_url:
            webbrowser.open(start_url)
        server()


if __name__ == "__main__":
    main()
