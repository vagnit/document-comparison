"""
Includes classes and functions to extract data from 
the company leaflet and label
"""

# Author: Evangelos Nittis <vagos333@gmail.com>

from urllib.parse import  urljoin
from re import sub
import os

import pandas as pd
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer,  LTFigure, LAParams 

LEAFLETS_FOLDER="tests/leaflet-examples/"  
BASE_URL = 'https://www.ema.europa.eu/'
REPORT_URL = urljoin(
    BASE_URL,
    'sites/default/files/Medicines_output_european_public_assessment_reports.xlsx',
)


def _extract_leaflet_path(product, language):
    """Extract the company leaflet document's path 
    for a specific product and language."""
    
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
            f'Parameter `product` should be one of {", ".join(products)}.\n\nInstead {product} was given.'
        )
        
    # Extract product path 
    product_path = os.path.join(LEAFLETS_FOLDER, product  + '_' + language  + '_leaflet.pdf')
    
    return product_path

    
def _extract_leaflet_to_content_comp(leaflet_pages):
    """Extract content from the company leaflet document."""

    content = {'text': [], 'images': []}

    # Iterate through pages
    for page in leaflet_pages:

        # Iterate through page elements
        for element in page:

            if isinstance(element, LTTextContainer):

                # # Iterate through lines of elements
                for text_line in element:
                    text = sub(r'\d.\s', '', text_line.get_text().splitlines()[0])
                    if not text.isnumeric():
                        content['text'].append(text)

            elif isinstance(element, LTFigure):
                for img in element:
                    content['images'].append(img.stream.get_data())

    return content


def _leaflet_to_dict_comp(path_to_file):     
    """Preparation of the dictionary of the company leaflet
    including keys and values"""

    dict_leaf_comp_in = dict()
    with open(path_to_file) as inputs:
        for line in inputs:
            if line.startswith("<b>"): 
                key = line.strip()[3:]
                dict_leaf_comp_in.setdefault(key,list())
            else:
                dict_leaf_comp_in[key].append(line.strip())
				  
	# Merge 
    dict_leaf_comp = dict()
    for key, vlist in dict_leaf_comp_in.items():
        dict_leaf_comp[key] = " ".join(vlist)
    
    return dict_leaf_comp


def convert_to_dict_comp(product, language='en'):
    """Convert the company leaflet document
    to a dictionary representation."""

    # Fetch pdf
    path = _extract_leaflet_path(product, language)

    # Extract pdf pages
    pages = list(
        extract_pages(path, laparams=LAParams(boxes_flow=None, 
                                              char_margin=5.0))
    )

    # Assign the pages found to the leaflet 
    leafleat_pages = pages 
    # label to be added

    # Extract content
    doc_dict_comp = { 
        # label to be added
        'leafleat': _extract_leaflet_to_content_comp(leafleat_pages),
    }

    return doc_dict_comp 

 