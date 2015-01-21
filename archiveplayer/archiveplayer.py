from pywb.framework.wsgi_wrappers import init_app, start_wsgi_server
from pywb.webapp.pywb_init import create_wb_router
from pywb.warc.cdxindexer import write_cdx_index
from pywb.webapp.handlers import WBHandler
from pywb.webapp.views import J2TemplateView

from pagedetect import PageDetectSortedWriter

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

no_wx = False
try:
    import wx
    wxFrame = wx.Frame
except:
    no_wx = True
    wxFrame = object

from waitress import serve

#=================================================================
PLAYER_URL = 'http://localhost:8090/replay/'

#=================================================================
class ArchivePlayer(object):
    CDX_NAME = 'index.cdx'

    DEFAULT_CONFIG_FILE = """
collections:
    {coll_name}:
        index_paths: {index_paths}

        wb_handler_class: !!python/name:archiveplayer.archiveplayer.ReplayHandler
    
archive_paths: {archive_path}

home_html: templates/index.html

search_html: templates/pagelist_search.html

port: 8090

framed_replay: true
"""

    def __init__(self, archivefile):
        self.archivefile = archivefile
        
        self.coll_name = 'replay'

        self.cdx_file = tempfile.NamedTemporaryFile(delete=False,
                                                    suffix='.cdx',
                                                    prefix='cdx')
        
        pagelist = self.update_cdx(self.cdx_file, archivefile)

        config = self._load_config()
        config['_pagelist'] = pagelist
        config['_archivefile'] = os.path.basename(self.archivefile)

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

    def _load_config(self):
        config_file = os.environ.get('PYWB_CONFIG_FILE', 'config.yaml')
        try:
            with open(config_file) as fh:
                contents = fh.read()
        except:
            contents = self.DEFAULT_CONFIG_FILE

        archive_dir = os.path.dirname(self.archivefile) + os.path.sep

        contents = contents.format(index_paths=self.cdx_file.name,
                                   archive_path=archive_dir,
                                   coll_name=self.coll_name)

        print('pywb config')
        print('===========')
        print(contents)

        return yaml.load(contents)

    def update_cdx(self, output_cdx, input_):
        """
        Output sorted, post-query resolving cdx from 'input_' warc(s)
        to 'output_cdx'. Write cdx to temp and rename to output_cdx
        when completed to ensure atomic updates of the cdx.
        """

        try:
            with open(input_, 'rb') as infile:
                writer = write_cdx_index(output_cdx, infile, os.path.basename(input_),
                                         sort=True,
                                         surt_ordered=True,
                                         append_post=True,
                                         include_all=True,
                                         writer_cls=PageDetectSortedWriter)
                output_cdx.flush()
        except Exception as exc:
            import traceback
            err_details = traceback.format_exc(exc)
            print err_details

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
        self.archivefile = config.get('_archivefile', '')
    
    def render_search_page(self, wbrequest, **kwargs):
        kwargs['pagelist'] = self.pagelist
        kwargs['archivefile'] = self.archivefile
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

        self.title = wx.StaticText(self, label='Web Archive Player v1.0')
        font = wx.Font(24, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)

        label = wx.StaticText(self, label='Archive Player Server running at:', pos=(4, 50))
        link = wx.HyperlinkCtrl(self, label=PLAYER_URL, url=PLAYER_URL, pos=(4, 70))
        
        self.archiveplayer = None

    def quit(self, cmd):
        self.Close()
        if self.archiveplayer:
            self.archiveplayer.close()

    def select_file(self):
        #style = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST# | wx.DIALOG_NO_PARENT
        #dialog = wx.DirDialog(top, 'Please select a directory containing archive files (WARC or ARC)', style=style)
        dialog = wx.FileDialog(parent=self,
                               message='Please select a web archive (WARC or ARC) file',
                               #wildcard='(*.warc.gz*.arc.gz*.warc*.arc)|*.warc.gz*.arc.gz*.warc*.arc',
                               wildcard='WARC or ARC (*.gz; *.warc; *.arc)|*.gz; *.warc; *.arc',
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
        else:
            path = None

        dialog.Destroy()
        return path


#=================================================================
def run_server(app):
    serve(app, port=8090, threads=10)
    #start_wsgi_server(archiveplayer.application, 'Wayback')


#=================================================================
def main():
    parser = ArgumentParser('Web Archive Player')
    parser.add_argument('archivefile', nargs='?')
    parser.add_argument('--headless', action='store_true',
                        help="Run without a GUI (defaults to true if wxPython not installed)")

    r = parser.parse_args()

    frame = None

    global no_wx
    if r.headless:
        no_wx = True

    if not no_wx:
        app = wx.App()
        frame = TopFrame(None)
        frame.init_controls()

    if r.archivefile:
        filename = r.archivefile
    else:
        if no_wx:
            print('Sorry, the wxPython toolkit must be installed to run in GUI mode')
            print('See http://wxpython.org/download.php for installation info')
            print('')
            print('You can still start webarchiveplayer directly by specifying a W/ARC file via the command line:')
            print(sys.argv[0] + ' <path to WARC>')
            return

        filename = frame.select_file()
        if filename:
            filename = filename.encode('utf-8')

    if not filename:
        return

    J2TemplateView.env_globals['packages'].append('archiveplayer')

    archiveplayer = ArchivePlayer(filename)

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
