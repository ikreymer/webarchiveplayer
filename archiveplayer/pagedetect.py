import os
import shutil
import json
import random
import subprocess

from io import BytesIO
from pywb.warc.cdxindexer import write_cdx_index, SortedCDXWriter
from datetime import datetime


#==================================================================
class PageDetectWriterMixin(object):
    EMPTY_DIGEST = '3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ'

    def __enter__(self):
        self.pages = []
        self.referers = set()
        self.count = 0

        self.is_guessing = True
        self.num_urls = 0

        return super(PageDetectWriterMixin, self).__enter__()

    def _possible_page(self, url, ts):
        # try some heuristics to determine if page

        # check for very long query, greater than the rest of url -- probably not a page
        parts = url.split('?', 1)
        if len(parts) == 2 and len(parts[1]) > len(parts[0]):
            return

        # skip robots.txt
        if parts[0].endswith('/robots.txt'):
            return

        self.pages.append(dict(url=url, ts=ts))

    def update_metadata(self, metadata, max_pages=500):
        if len(self.pages) >= max_pages:
            metadata['pages'] = random.sample(self.pages, max_pages)
        else:
            metadata['pages'] = self.pages

        metadata['num_urls'] = self.count

    def write(self, entry, filename):
        if entry.record.rec_type in ('response', 'revisit'):
            self.count = self.count + 1

        if entry.record.rec_type == 'request':
            return

        # if warcinfo is first, attempt to extract page info
        if entry.record.rec_type == 'warcinfo':
            #if self.count == 0:
            #    if self.parse_page_info(entry):
            #        self.is_guessing = False
            return

        elif entry.record.content_type == 'application/warc-fields':
            return

        # if not guessing, just pass to super
        if self.is_guessing:
            if (entry['mime'] in ('text/html', 'text/plain')  and
                entry['status'] == '200' and
                entry['digest'] != self.EMPTY_DIGEST):

                self._possible_page(entry['url'], entry['timestamp'])

            elif entry['url'] in self.referers:
                self._possible_page(entry['url'], entry['timestamp'])

            if entry.get('_referer'):
                self.referers.add(entry['_referer'])

        super(PageDetectWriterMixin, self).write(entry, filename)

    def parse_page_info(self, entry):
        if (entry.record.content_type != 'application/warc-fields'):
            return False

        metadata = self.extract_metadata(entry.warcinfo)
        if not metadata:
            return False

        self.pages.extend(metadata.get('pages', []))
        self.num_urls += metadata.get('num_urls', 0)
        return True

    @staticmethod
    def extract_metadata(buff):
        for line in buff.split('\n'):
            parts = line.split(': ', 1)
            if parts[0] != 'json-metadata':
                continue

            try:
                metadata = json.loads(parts[1])
                return metadata
            except Exception as exc:
                import traceback
                err_details = traceback.format_exc(exc)
                print err_details

                print 'error parsing metadata: ', parts[1]
                continue


class PageDetectSortedWriter(PageDetectWriterMixin, SortedCDXWriter):
    pass

