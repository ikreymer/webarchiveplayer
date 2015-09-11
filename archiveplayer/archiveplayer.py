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
    wxFrame = wx.Frame
except:
    no_wx = True
    wxFrame = object

from waitress import serve

#=================================================================
PORT = 8090
PLAYER_URL_TEMP = 'http://localhost:{0}/'
PLAYER_URL = 'http://localhost:8090/'

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

        pagelist = self.update_cdx(self.cdx_file, archivefiles)

        config = self._load_config()
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

    def _load_config(self):
        config_file = os.environ.get('PYWB_CONFIG_FILE', 'config.yaml')
        try:
            with open(config_file) as fh:
                contents = fh.read()
        except:
            contents = self.DEFAULT_CONFIG_FILE

        #archive_dir = os.path.dirname(self.archivefile) + os.path.sep
        archive_path = self.path_index.name

        contents = contents.format(index_paths=self.cdx_file.name,
                                   archive_path=archive_path,
                                   coll_name=self.coll_name)

        print('pywb config')
        print('===========')
        print(contents)

        return yaml.load(contents)

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


#=================================================================
class TopFrame(wxFrame):
    def init_controls(self):
        self.menu_bar  = wx.MenuBar()
        self.help_menu = wx.Menu()

        #self.help_menu.Append(wx.ID_ABOUT,   menuTitle_about)
        self.help_menu.Append(wx.ID_EXIT,   "&QUIT")
        self.menu_bar.Append(self.help_menu, "File")

        #self.Bind(wx.EVT_MENU, self.displayAboutMenu, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.quit, id=wx.ID_EXIT)
        self.SetMenuBar(self.menu_bar)

        self.title = wx.StaticText(self, label='Web Archive Player ' + __version__)
        font = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)

        pywb_info = wx.StaticText(self, label='(pywb {0})'.format(pywb_version), pos=(4, 20))
        font = wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        pywb_info.SetFont(font)

        label = wx.StaticText(self, label='Archive Player Server running at:', pos=(4, 50))
        link = wx.HyperlinkCtrl(self, id=0, label=PLAYER_URL, url=PLAYER_URL, pos=(4, 70))

        info_label = wx.StaticText(self, label='For more info about Web Archive Player, please visit:', pos=(4, 100))
        info_link = wx.HyperlinkCtrl(self, id=0, label=INFO_URL, url=INFO_URL, pos=(4, 120))

        self.archiveplayer = None

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
def run_server(app):
    serve(app, port=PORT, threads=10)
    #start_wsgi_server(archiveplayer.application, 'Wayback')


#=================================================================
def ensure_close(archiveplayer):
    print('Deleting Temps')
    if archiveplayer:
        archiveplayer.close()


#=================================================================
def main():
    parser = ArgumentParser('Web Archive Player')
    parser.add_argument('archivefiles', nargs='*')
    parser.add_argument('--port', nargs='?', default=8090, type=int)
    parser.add_argument('-v', '--version', action='store_true')
    parser.add_argument('--headless', action='store_true',
                        help="Run without a GUI (defaults to true if wxPython not installed)")

    r = parser.parse_args()

    if r.version:
        print(__version__)
        sys.exit(0)

    global PORT
    PORT = r.port

    global PLAYER_URL_TEMP
    global PLAYER_URL
    PLAYER_URL = PLAYER_URL_TEMP.format(PORT)

    frame = None

    global no_wx
    if r.headless:
        no_wx = True

    if not no_wx:
        app = wx.App()
        frame = TopFrame(None)
        frame.init_controls()

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

    if frame:
        frame.archiveplayer = archiveplayer

        server = Thread(target=run_server, args=(archiveplayer.application,))
        server.daemon = True
        server.start()

        webbrowser.open(PLAYER_URL)

        frame.Show()
        app.MainLoop()
    else:
        webbrowser.open(PLAYER_URL)
        run_server(archiveplayer.application)

if __name__ == "__main__":
    main()
