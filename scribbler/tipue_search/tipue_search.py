# -*- coding: utf-8 -*-
"""
Tipue Search
============

A Pelican plugin to serialize generated HTML to JSON
that can be used by jQuery plugin - Tipue Search.

Copyright (c) Talha Mansoor
"""

from __future__ import unicode_literals

import os.path
import json
from bs4 import BeautifulSoup
from codecs import open
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from pelican import signals


class Tipue_Search_JSON_Generator(object):

    def __init__(self, context, settings, path, theme, output_path, *null):

        self.output_path = output_path
        self.context = context
        self.siteurl = settings.get('SITEURL')
        self.tpages = settings.get('TEMPLATE_PAGES')
        self.relative = settings.get('RELATIVE_URLS')
        self.output_path = output_path
        self.json_nodes = []


    def create_json_node(self, page):

        if getattr(page, 'status', 'published') != 'published':
            return

        soup_title = BeautifulSoup(page.title.replace('&nbsp;', ' '), 'html.parser')
        page_title = soup_title.get_text(' ', strip=True).replace('“', '"').replace('”', '"').replace('’', "'").replace('^', '&#94;')

        soup_text = BeautifulSoup(page.content, 'html.parser')
        page_text = soup_text.get_text(' ', strip=True).replace('“', '"').replace('”', '"').replace('’', "'").replace('¶', ' ').replace('^', '&#94;')
        page_text = ' '.join(page_text.split())

        if getattr(page, 'category', 'None') == 'None':
            page_category = ''
        else:
            page_category = page.category.name

        if not self.relative:
            page_url = self.siteurl + '/' + page.url
        else:
            page_url = page.url

        node = {'title': page_title,
                'text': page_text,
                'tags': page_category,
                'loc': page_url}

        self.json_nodes.append(node)


    def create_tpage_node(self, srclink):

        srcfile = open(os.path.join(self.output_path, self.tpages[srclink]))
        soup = BeautifulSoup(srcfile, 'html.parser')
        page_text = soup.get_text()

        # What happens if there is not a title.
        if soup.title is not None:
            page_title = soup.title.string
        else:
            page_title = ''

        # Should set default category?
        page_category = ''

        if not self.relative:
            page_url = urljoin(self.siteurl, self.tpages[srclink])
        else:
            page_url = sefl.tpages[srclink]

        node = {'title': page_title,
                'text': page_text,
                'tags': page_category,
                'loc': page_url}
        
        self.json_nodes.append(node)


    def generate_output(self, writer):
        path = os.path.join(self.output_path, 'tipuesearch_content.js')

        pages = self.context['pages'] + self.context['articles']

        for article in self.context['articles']:
            pages += article.translations

        for srclink in self.tpages:
            self.create_tpage_node(srclink)

        for page in pages:
            self.create_json_node(page)
        root_node = {'pages': self.json_nodes}

        output = json.dumps(root_node, separators=(',', ':'), ensure_ascii=False)
        output = 'var tipuesearch = ' + output
        with open(path, 'w', encoding='utf-8') as fd:
            fd.write(output)


def get_generators(generators):
    return Tipue_Search_JSON_Generator


def register():
    signals.get_generators.connect(get_generators)
