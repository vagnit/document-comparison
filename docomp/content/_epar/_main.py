"""
Includes the main function to download the latest EPAR document and extract
content from it.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>

from ._downloading import EPARDownloader
from ._extraction import (
    SectionExtractor,
    LabellingHTMLExtractor,
    LeafletHTMLExtractor,
    ImagesExtractor,
)


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
            'html': LeafletHTMLExtractor(leaflet_pages).extracted_data_,
            'images': ImagesExtractor(leaflet_pages).extracted_data_,
        },
    }

    return doc_dict
