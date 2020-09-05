"""
Includes classes and functions to download the latest EPAR document.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>

from urllib.parse import urlparse, urljoin
from urllib.request import urlopen, urlretrieve

import pandas as pd
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams

from .._utils import check_param, BaseDownloader
from ... import CONFIG

CONFIG = CONFIG['content']['epar']['downloading']


class EPARDownloader(BaseDownloader):
    """Class to download EPAR pdf document."""

    EPAR_CONFIG = CONFIG['epar_downloader']
    REPORT_URL_ = urljoin(
        CONFIG['base_url'].get(str), EPAR_CONFIG['report_url'].get(str)
    )
    PRODUCT_URL_ = EPAR_CONFIG['product_url'].get(str)
    SKIPROWS_ = EPAR_CONFIG['skiprows'].get(int)
    USECOLS_ = EPAR_CONFIG['usecols'].get(str)
    BOXES_FLOW_ = EPAR_CONFIG['boxes_flow'].get()
    CHAR_MARGIN_ = EPAR_CONFIG['char_margin'].get(float)

    def __init__(self, product, language='en'):
        self.product = product
        self.language = language

    @property
    def report_(self):
        """Get the report excel file."""
        report = pd.read_excel(
            self.REPORT_URL_, skiprows=self.SKIPROWS_, usecols=self.USECOLS_
        )
        return report[report['Authorisation status'] == 'Authorised']

    @property
    def available_products_(self):
        """Get the available products."""
        return self.report_['Medicine name'].unique()

    @property
    def main_url_(self):
        """Get the EPAR document main url for a specific product."""

        # Check product
        self.product_ = check_param(
            'product', self.product.capitalize(), self.available_products_
        )

        # Extract product url
        main_url = self.report_.loc[
            self.report_['Medicine name'] == self.product_, 'URL'
        ].values[0]

        return main_url

    @property
    def download_url_(self):
        """Get the EPAR's document download url for a specific product and
        language."""

        # Get EPAR document html
        html = urlopen(self.main_url_)
        bsObj = BeautifulSoup(html.read(), features='html.parser')

        # Get available urls
        urls = {}
        for el in bsObj.find_all('a'):
            url = urlparse(el.get('href'))
            url_start = self.PRODUCT_URL_.format(self.product_.lower())
            if str(url.path).startswith(url_start):
                urls[
                    url.path.split('/')[-1].split('_')[-1].replace('.pdf', '')
                ] = url.geturl()

        # Check language
        self.available_languages_ = urls.keys()
        self.language_ = check_param(
            'language', self.language.lower(), self.available_languages_
        )

        return urls[self.language_]

    def download(self):
        """Download EPAR pdf."""
        path = urlretrieve(self.download_url_)[0]
        pages = list(
            extract_pages(
                path,
                laparams=LAParams(
                    boxes_flow=self.BOXES_FLOW_, char_margin=self.CHAR_MARGIN_
                ),
            )
        )
        return pages
