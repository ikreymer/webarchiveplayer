from pywb.framework.wsgi_wrappers import init_app, start_wsgi_server
from pywb.webapp.pywb_init import create_wb_router

import os
import sys
import yaml
from datetime import datetime

from pywb.warc import cdxindexer
from argparse import ArgumentParser

import webbrowser


#=================================================================
class ArchivePlayer(object):
    CDX_NAME = 'index.cdx'

    DEFAULT_CONFIG_FILE = """
collections:
    {coll_name}: {index_paths}

archive_paths: {archive_path}

port: 8090

framed_replay: true
    """

    def __init__(self, archive_dir):
        self.archive_dir = archive_dir.rstrip(os.path.sep)

        self.cdx_file = os.path.join(archive_dir, self.CDX_NAME)
        self.update_cdx(self.cdx_file, archive_dir)

        config = self._load_config()

        self.application = init_app(create_wb_router,
                                    load_yaml=False,
                                    config=config)

    def _load_config(self):
        config_file = os.environ.get('PYWB_CONFIG_FILE', 'config.yaml')
        try:
            with open(config_file) as fh:
                contents = fh.read()
        except:
            contents = self.DEFAULT_CONFIG_FILE

        coll_name = os.path.basename(self.archive_dir)
        if not coll_name:
            coll_name = 'replay'

        contents = contents.format(index_paths=self.archive_dir,
                                   archive_path=self.archive_dir,
                                   coll_name=coll_name)

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
        # Run cdx indexer
        temp_cdx = output_cdx + '.tmp.' + self.timestamp20()
        indexer_args = ['-s', '-p', temp_cdx, input_]

        try:
            cdxindexer.main(indexer_args)
        except Exception as exc:
            import traceback
            err_details = traceback.format_exc(exc)
            print err_details

            os.remove(temp_cdx)
            return False
        else:
            os.rename(temp_cdx, output_cdx)
            return True

    @staticmethod
    def timestamp20():
        """
        Create 20-digit timestamp, useful to timestamping temp files
        """
        now = datetime.utcnow()
        return now.strftime('%Y%m%d%H%M%S%f')


#=================================================================
def select_dir():
    import wx
    app = wx.App(None)
    style = wx.DD_DIR_MUST_EXIST
    dialog = wx.DirDialog(None, 'Please select a directory containing archive files (WARC or ARC)', style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = None
    dialog.Destroy()
    return path

#=================================================================
def main():
    parser = ArgumentParser('Web Archive Player')
    parser.add_argument('archivedir', nargs='?')

    r = parser.parse_args()

    if r.archivedir:
        dir_name = r.archivedir
    else:
        dir_name = select_dir()
        dir_name = dir_name.encode('utf-8')

    if not dir_name:
        return

    archiveplayer = ArchivePlayer(dir_name)
    webbrowser.open('http://localhost:8090/')
    start_wsgi_server(archiveplayer.application, 'Wayback')


if __name__ == "__main__":
    main()
