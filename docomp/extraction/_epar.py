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

BASE_URL = 'https://www.ema.europa.eu/'
REPORT_URL = urljoin(
    BASE_URL,
    'sites/default/files/Medicines_output_european_public_assessment_reports.xlsx',
)
MIN_LENGTH = 5
MIN_UPPER_RATIO = 0.7


def _extract_product_url(product):
    """Extract the EPAR document's url for a specific product."""

    # Capitalize product
    try:
        product = product.capitalize()
    except AttributeError:
        raise TypeError(
            f'Parameter `product` should be a string. Got {type(product)} instead.'
        )

    # Read excel file
    data = pd.read_excel(REPORT_URL, skiprows=8, usecols='B,H,AD')

    # Keep authorised state
    data = data[data['Authorisation status'] == 'Authorised']

    # Validate product name
    products = data['Medicine name'].unique()
    if product not in products:
        raise ValueError(
            f'Parameter `product` should be one of {", ".join(products)}.\n\n'
            f'Instead {product} was given.'
        )

    # Extract product url
    product_url = data.loc[data['Medicine name'] == product, 'URL'].values[0]

    return product_url


def _extract_product_language_url(product, language):
    """Extract the EPAR document's url for a specific product and
    language."""

    # Convert language to lower case
    try:
        language = language.lower()
    except AttributeError:
        raise TypeError(
            f'Parameter `language` should be a string. Got {type(language)} instead.'
        )

    # Get EPAR document html
    html = urlopen(_extract_product_url(product))
    bsObj = BeautifulSoup(html.read(), features='html.parser')

    # Get available urls
    urls = {}
    for el in bsObj.find_all('a'):
        url = urlparse(el.get('href'))
        url_start = (
            f'/documents/product-information/{product.lower()}-epar-product-information'
        )
        if str(url.path).startswith(url_start):
            urls[
                url.path.split('/')[-1].split('_')[-1].replace('.pdf', '')
            ] = url.geturl()

    # Check language
    languages = urls.keys()
    if language not in languages:
        raise ValueError(
            f'Parameter `language` should be one of {", ".join(languages)}.\n\n'
            f'Instead {language} was given.'
        )

    return urls[language]


def _identify_sections(pages):
    """Identify the leaflet and labelling sections."""
    sections = []

    # Iterate through pages
    for page in pages:

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

    return [sections[0], sections[-1]]


class HTMLExtractor:
    """Class to extract HTML from pdf pages."""

    def __init__(self, pages):
        self.pages = pages

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
                                text.isupper() and length >= MIN_LENGTH
                            ) or upper_ratio > MIN_UPPER_RATIO:
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

    def apply(self):
        """Apply the HTML extraction."""
        self._extract_elements()._modify_elements()
        self.html_ = ''.join(self.html_)
        return self


class ImagesExtractor:
    """Class to extract images from pdf pages."""

    def __init__(self, pages):
        self.pages = pages

    def apply(self):

        self.images_ = []

        # Iterate through pages
        for page in self.pages:

            # Iterate through page elements
            for element in page:

                if isinstance(element, LTFigure):
                    for img in element:
                        self.images_.append(img.stream.get_data())

        return self


def convert_epar_to_dict(product, language='en'):
    """Convert the EPAR document to a dictionary representation."""

    # Fetch pdf
    path = urlretrieve(_extract_product_language_url(product, language))[0]

    # Extract pdf pages
    pages = list(
        extract_pages(path, laparams=LAParams(boxes_flow=None, char_margin=10.0))
    )

    # Identify sections
    labelling_num, leaflet_num = _identify_sections(pages)
    labelling_pages = pages[(labelling_num + 1): leaflet_num]
    leafleat_pages = pages[(leaflet_num + 1):]

    # Extract content
    doc_dict = {
        'labelling': {
            'html': HTMLExtractor(labelling_pages).apply(),
            'images': ImagesExtractor(labelling_pages).apply(),
        },
        'leafleat': {
            'html': HTMLExtractor(leafleat_pages).apply(),
            'images': ImagesExtractor(leafleat_pages).apply(),
        },
    }

    return doc_dict
