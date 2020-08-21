"""
Includes classes and functions to download the latest EPAR document and extract
data from it.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>

from urllib.parse import urlparse, urljoin
from urllib.request import urlopen, urlretrieve

import pandas as pd
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTImage

BASE_URL = 'https://www.ema.europa.eu/'
REPORT_URL = urljoin(BASE_URL, 'sites/default/files/Medicines_output_european_public_assessment_reports.xlsx')


def _extract_product_url(product):
    """Extract the EPAR document's url for a specific product."""

    # Read excel file
    data = pd.read_excel(REPORT_URL, skiprows=8, usecols='B,H,AD')
    
    # Keep authorised state
    data = data[data['Authorisation status'] == 'Authorised']

    # Validate product name
    products = data['Medicine name'].unique()
    if product not in products:
        raise ValueError(f'Parameter `product` should be one of {", ".join(products)}.\n\nInstead {product} was given.')
    
    # Extract product url
    product_url = data.loc[data['Medicine name'] == product, 'URL'].values[0]

    return product_url


def _extract_product_language_url(product, language):
    """Extract the EPAR document's url for a specific product and language."""
    
    # Get EPAR document html
    html = urlopen(_extract_product_url(product))
    bsObj = BeautifulSoup(html.read(), features='html.parser')
    
    # Get available urls
    urls = {}
    for el in bsObj.find_all('a'):
        url = urlparse(el.get('href'))
        url_start = f'/documents/product-information/{product.lower()}-epar-product-information'
        if str(url.path).startswith(url_start):
            urls[url.path.split('/')[-1].split('_')[-1].replace('.pdf', '')] = url.geturl()
    
    # Check language
    languages = urls.keys()
    if language not in languages:
        raise ValueError(f'Parameter `language` should be one of {", ".join(languages)}.\n\nInstead {language} was given.')
    
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


def _labelling_to_dict(labelling_pages):
    """Convert the labelling section of EPAR document to a dictionary representation."""
    pass


def _leaflet_to_dict(leaflet_pages):
    """Convert the leaflet section of EPAR document to a dictionary representation."""
    pass


def _convert_to_dict(product, language):
    """Convert the EPAR document to a dictionary representation."""
    
    # Fetch pdf
    path = urlretrieve(_extract_product_language_url(product, language))[0]

    # Extract pdf pages
    pages = list(extract_pages(path))

    # Identify sections
    labelling_num, leaflet_num = _identify_sections(pages)
    labelling_pages = pages[(labelling_num + 1):leaflet_num]
    leafleat_pages = pages[(leaflet_num + 1):]
            
    # Extract content
    doc_dict = {
        'labelling': _labelling_to_dict(labelling_pages),
        'leafleat': _leaflet_to_dict(leafleat_pages)
    }

    return doc_dict
    