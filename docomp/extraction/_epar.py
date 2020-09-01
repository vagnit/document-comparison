"""
Includes classes and functions to download the latest EPAR document and extract
data from it.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>

from urllib.parse import urlparse, urljoin
from urllib.request import urlopen, urlretrieve
from re import match

import pandas as pd
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTFigure, LAParams
from confuse import Configuration

from ._utils import BaseDownloader, BaseExtractor
from .. import CONFIG

CONFIG = CONFIG['extraction']['epar']


class EPARDownloader(BaseDownloader):
    """Class to download EPAR pdf document."""

    REPORT_URL_ = urljoin(CONFIG['base_url'].get(str), CONFIG['epar_downloader']['report_url'].get(str))
    PRODUCT_URL_ = CONFIG['epar_downloader']['product_url'].get(str)
    SKIPROWS_ = CONFIG['epar_downloader']['skiprows'].get(int)
    USECOLS_ = CONFIG['epar_downloader']['usecols'].get(str)
    BOXES_FLOW_ = CONFIG['epar_downloader']['boxes_flow'].get()
    CHAR_MARGIN_ = CONFIG['epar_downloader']['char_margin'].get(float)

    def __init__(self, product, language='en'):
        self.product = product
        self.language = language

    @property
    def report_(self):
        """Get the report excel file."""
        report = pd.read_excel(self.REPORT_URL_, skiprows=self.SKIPROWS_, usecols=self.USECOLS_)
        return report[report['Authorisation status'] == 'Authorised']
    
    @property
    def available_products_(self):
        """Get the available products."""
        return self.report_['Medicine name'].unique()

    @property
    def main_url_(self):
        """Get the EPAR document main url for a specific product."""

        # Check product
        self.product_ = self._check_param('product', self.product.capitalize(), self.available_products_)

        # Extract product url
        main_url = self.report_.loc[self.report_['Medicine name'] == self.product_, 'URL'].values[0]

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
            url_start = (
                self.PRODUCT_URL_.format(self.product_.lower())
            )
            if str(url.path).startswith(url_start):
                urls[
                    url.path.split('/')[-1].split('_')[-1].replace('.pdf', '')
                ] = url.geturl()

        # Check language
        self.available_languages_ = urls.keys()
        self.language_ = self._check_param('language', self.language.lower(), self.available_languages_)

        return urls[self.language_]
    
    def download(self):
        """Download EPAR pdf."""
        path = urlretrieve(self.download_url_)[0]
        pages = list(
            extract_pages(path, laparams=LAParams(boxes_flow=self.BOXES_FLOW_, char_margin=self.CHAR_MARGIN_))
        )
        return pages


class SectionExtractor(BaseExtractor):
    """Class to extract the labelling and leaflet sections from EPAR pdf
    document."""

    def extract(self):
        """Extract leaflet and labelling sections."""

        sections = []

        # Iterate through pages
        for page in self.pages:

            # Non-empty lines
            lines = []

            # Iterate through page elements
            for element in page:
                if isinstance(element, LTTextContainer):

                    # # Iterate through lines of elements
                    for text_line in element:
                        text = text_line.get_text().splitlines()
                        if text != [' ']:
                            lines.append(text)

            # Identify sections
            if len(lines) == 2:
                sections.append(page.pageid - 1)
        
        # Sections page numbers
        self.first_num_, self.second_num_ = sections[0], sections[-1]

        # Sections
        first_section, second_section = self.pages[(self.first_num_ + 1): self.second_num_], self.pages[(self.second_num_ + 1):]

        return first_section, second_section


class LabellingHTMLExtractor(BaseExtractor):
    """Class to extract HTML from the labelling section of EPAR."""

    MIN_LENGTH_ = CONFIG['labelling_html_extractor']['min_length'].get(int)
    MIN_UPPER_CASE_RATIO_ = CONFIG['labelling_html_extractor']['min_upper_case_ratio'].get(float)

    def _extract_elements(self):
        """Extract HTML elements."""
        self.html_ = []

        # Iterate through pages
        for page in self.pages:

            # Iterate through page elements
            for element in page:

                if isinstance(element, LTTextContainer):

                    # Iterate through lines of elements
                    for text_line in element:
                        text = ' '.join(text_line.get_text().split())
                        if text and not text.isdigit():
                            length = sum(1 for char in text if char.isupper())
                            upper_ratio = length / len(''.join(text.split()))
                            if (
                                text.isupper() and length >= self.MIN_LENGTH_
                            ) or upper_ratio > self.MIN_UPPER_CASE_RATIO_:
                                html_element = f'<p><b>{text}</b></p>'
                            else:
                                html_element = f'<p>{text}</p>'
                            self.html_.append(html_element)

        return self

    def _modify_elements(self):
        """Modify extracted HTML elements."""
        html = self.html_[0:1]
        for prev_element, element, next_element in list(
            zip(self.html_[0:-2], self.html_[1:-1], self.html_[2:])
        ):
            prev_match = match(
                r'\d+.', prev_element.replace('<p><b>', '').replace('</b></p>', '')
            )
            next_match = match(
                r'\d+.', next_element.replace('<p><b>', '').replace('</b></p>', '')
            )
            if (
                prev_match
                and next_match
                and int(next_match.group()[:-1]) - int(prev_match.group()[:-1]) == 1
            ):
                element = element.replace('<b>', '').replace('</b>', '')
            html.append(element)

        self.html_ = html + [next_element]

        return self

    def extract(self):
        """Extract HTML."""
        self._extract_elements()._modify_elements()
        return self.html_


class ImagesExtractor(BaseExtractor):
    """Class to extract images from pdf pages."""

    def extract(self):

        images = []

        # Iterate through pages
        for page in self.pages:

            # Iterate through page elements
            for element in page:

                if isinstance(element, LTFigure):
                    for img in element:
                        images.append(img.stream.get_data())

        return images


def extract_epar_content(product, language='en'):
    """Download and extract content from the EPAR document."""

    pages = EPARDownloader(product, language).downloaded_data_

    # Identify sections
    labelling_pages, leaflet_pages = SectionExtractor(pages).extracted_data_

    # Extract content
    doc_dict = {
        'labelling': {
            'html': LabellingHTMLExtractor(labelling_pages).extracted_data_,
            'images': ImagesExtractor(labelling_pages).extracted_data_,
        },
        'leafleat': {
            'html': LabellingHTMLExtractor(labelling_pages).extracted_data_,
            'images': ImagesExtractor(labelling_pages).extracted_data_,
        },
    }

    return doc_dict
