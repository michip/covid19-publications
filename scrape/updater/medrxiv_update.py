import json
import re

import requests
from bs4 import BeautifulSoup

from data.models import DataSource
from datetime import datetime
from scrape.updater.data_updater import ArticleDataPoint, DataUpdater


_MEDRXIV_PAPERHOST_NAME = 'medRxiv'
_BIORXIV_PAPERHOST_NAME = 'bioRxiv'
_MEDRXIV_PAPERHOST_URL = 'https://www.medrxiv.org'
_BIORXIV_PAPERHOST_URL = 'https://www.biorxiv.org'
_MEDRXIV_DATA_PRIORITY = 1


class MedrxivDataPoint(ArticleDataPoint):
    def __init__(self, raw_article_json):
        super().__init__()
        self.raw_article = raw_article_json
        self._article_soup = None

    def _setup_article_soup(self):
        if not self._article_soup:
            response = requests.get(self.url)
            self._article_soup = BeautifulSoup(response.text, 'html.parser')
            self.redirected_url = response.url

    @property
    def doi(self):
        return self.raw_article['rel_doi']

    @property
    def title(self):
        return self.raw_article['rel_title']

    @property
    def abstract(self):
        return self.raw_article['rel_abs']

    @property
    def extract_authors(self):
        self._setup_article_soup()

        author_webelements = self._article_soup.find(
            'span', attrs={'class': 'highwire-citation-authors'}
        ).find_all('span', recursive=False)

        authors = []
        for author_webelement in author_webelements:
            try:
                firstname = author_webelement.find('span', attrs={'class': 'nlm-given-names'}).text
                lastname = author_webelement.find('span', attrs={'class': 'nlm-surname'}).text
                authors.append((lastname, firstname))
            except AttributeError:
                # Ignore collaboration groups, listed in authors list
                continue
        return authors

    @property
    def extract_content(self):
        return None

    @property
    def data_source_name(self):
        return DataSource.MEDBIORXIV_DATASOURCE_NAME

    @property
    def data_source_priority(self):
        return _MEDRXIV_DATA_PRIORITY

    @property
    def paperhost_name(self):
        site = self.raw_article['rel_site']
        if site == "medrxiv":
            return _MEDRXIV_PAPERHOST_NAME
        elif site == "biorxiv":
            return _BIORXIV_PAPERHOST_NAME
        else:
            return None

    @property
    def paperhost_url(self):
        if self.paperhost_name == _MEDRXIV_PAPERHOST_NAME:
            return _MEDRXIV_PAPERHOST_URL
        else:
            return _BIORXIV_PAPERHOST_URL

    @property
    def published_at(self):
        return datetime.strptime(self.raw_article['rel_date'], "%Y-%m-%d").date()

    @property
    def url(self):
        return self.raw_article['rel_link']

    @property
    def pdf_url(self):
        self._setup_article_soup()

        dl_element = self._article_soup.find('a', attrs={'class': 'article-dl-pdf-link link-icon'})
        if dl_element and dl_element.has_attr('href'):
            relative_url = dl_element['href']
            return self.paperhost_url + relative_url
        else:
            return None

    @property
    def version(self):
        self._setup_article_soup()

        version_match = re.match(r'^\S+v(\d+)$', self.redirected_url)
        if version_match:
            return version_match.group(1)
        else:
            return '1'

    @property
    def is_preprint(self):
        return True

    @property
    def category_name(self):
        self._setup_article_soup()
        categories = self._article_soup.find_all('span', {'class': 'highwire-article-collection-term'})
        if len(categories) == 0:
            return "Unknown"
        else:
            return categories[0].text.strip()


class MedrxivUpdater(DataUpdater):
    _COVID_JSON_URL = 'https://connect.medrxiv.org/relate/collection_json.php?grp=181'

    @property
    def _data_source_name(self):
        return DataSource.MEDBIORXIV_DATASOURCE_NAME

    def __init__(self, log=print):
        super().__init__(log)
        self._article_json = self._get_article_json()

    def _get_article_json(self):
        try:
            response = requests.get(self._COVID_JSON_URL)
            return json.loads(response.text)['rels']
        except requests.exceptions.ConnectionError:
            raise Exception("Unable to download medRxiv COVID-19 article list JSON")

    @property
    def _data_points(self):
        for article in self._article_json:
            yield MedrxivDataPoint(raw_article_json=article)

    def _get_data_point(self, doi):
        try:
            return MedrxivDataPoint(raw_article_json=next(x for x in self._article_json if x['rel_doi'] == doi))
        except StopIteration:
            return None
