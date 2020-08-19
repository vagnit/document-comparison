"""
Includes classes and functions to download the latest EPAR document and extract
data from it.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>

from urllib.request import urlopen, urlretrieve

import pandas as pd
from bs4 import BeautifulSoup
import PyPDF2

EMA_REPORT_URL = 'https://www.ema.europa.eu/sites/default/files/Medicines_output_european_public_assessment_reports.xlsx'


def _extract_product_url(product):
    """Extract the url for a specific product."""

    # Read excel file
    data = pd.read_excel(EMA_REPORT_URL, skiprows=8, usecols='B,H,AD')
    
    # Filter product and keep authorised state
    prod_mask = data['Medicine name'] == product
    auth_mask = data['Authorisation status'] == 'Authorised'
    
    # Extract product url
    product_url = data.loc[prod_mask & auth_mask, 'URL'].values[0]

    return product_url


def _extract_epar_url(product, language):
    """Extract the EPAR document url by product and language."""
    
    # Extract product url
    product_url = _extract_product_url(product)
    
    # Return EPAR document url from html
    html = urlopen(product_url)
    bsObj = BeautifulSoup(html.read(), features='html.parser')
    for el in bsObj.find_all('a'):
        url = el.get('href')
        if url is not None and 'product-information' in url and url.endswith(f'_{language}.pdf'):
            return url
    

def _fetch_epar_pdf(product, language):
    """Fetch the EPAR document pdf by product and language."""
    
    # Extract EPAR document url
    epar_url = _extract_epar_url(product, language)
    
    # Create file object
    path = urlretrieve(epar_url)[0]
    file = open(path, 'rb')
    
    # Create pdf object
    pdf = PyPDF2.PdfFileReader(file)
    
    return pdf
