"""
Test the _downloading module.
"""

from os import listdir
from os.path import join

import pytest
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams

from docomp.content._epar._extraction import SectionExtractor, LabellingHTMLExtractor
from docomp import CONFIG

EXTRACTION_PATH = join('docomp', 'content', '_epar', 'tests', 'resources', 'extraction')
CONFIG = CONFIG['content']['epar']['downloading']
BOXES_FLOW = CONFIG['epar_downloader']['boxes_flow'].get()
CHAR_MARGIN = CONFIG['epar_downloader']['char_margin'].get(float)
PDFS = sorted(
    [file_name for file_name in listdir(EXTRACTION_PATH) if file_name.endswith('.pdf')]
)
PRODUCTS_LANGUAGES = [tuple(pdf.replace('.pdf', '').split('_')) for pdf in PDFS]
PAGES_MAPPING = {
    (product, language): list(
        extract_pages(
            join(EXTRACTION_PATH, f'{product}_{language}.pdf'),
            laparams=LAParams(boxes_flow=BOXES_FLOW, char_margin=CHAR_MARGIN),
        )
    )
    for product, language in PRODUCTS_LANGUAGES
}
SECTIONS_NUMS_MAPPING = dict(zip(PRODUCTS_LANGUAGES, [[17, 21], [17, 23]]))


@pytest.mark.parametrize('product,language', PRODUCTS_LANGUAGES)
def test_section_extractor(product, language):
    """Test the section extractor."""
    section_extractor = SectionExtractor(PAGES_MAPPING[(product, language)])
    section_extractor.extracted_data_
    assert (
        section_extractor.sections_nums_ == SECTIONS_NUMS_MAPPING[(product, language)]
    )


@pytest.mark.parametrize('product,language', PRODUCTS_LANGUAGES)
def test_labelling_html_extractor(product, language):
    """Test the labelling html extractor."""
    first_section, _ = SectionExtractor(
        PAGES_MAPPING[(product, language)]
    ).extracted_data_
    labelling_html_extractor = LabellingHTMLExtractor(first_section)
    extracted_html = BeautifulSoup(
        labelling_html_extractor.extracted_data_, features='html.parser'
    ).find_all('p')
    with open(join(EXTRACTION_PATH, f'{product}_{language}.html'), 'r') as html_file:
        expected_html = BeautifulSoup(
            html_file.read(), features='html.parser'
        ).find_all('p')
    assert extracted_html == expected_html
