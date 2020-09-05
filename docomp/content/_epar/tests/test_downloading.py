"""
Test the _downloading module.
"""

from os import listdir
from os.path import join
from urllib.parse import urljoin

import pytest
import pandas as pd
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams

from docomp.content._utils import check_param
from docomp.content._epar._downloading import EPARDownloader
from docomp import CONFIG

DOWNLOADING_PATH = join(
    'docomp', 'content', '_epar', 'tests', 'resources', 'downloading'
)
REPORT_PATH = join(DOWNLOADING_PATH, 'report.xlsx')
PDFS = [
    file_name for file_name in listdir(DOWNLOADING_PATH) if file_name.endswith('.pdf')
]
PRODUCTS_LANGUAGES = [pdf.replace('.pdf', '').split('_')[::2] for pdf in PDFS]
CONFIG = CONFIG['content']['epar']['downloading']
BASE_URL = CONFIG['base_url'].get(str)
PRODUCT_URL = CONFIG['epar_downloader']['product_url'].get(str)
BOXES_FLOW = CONFIG['epar_downloader']['boxes_flow'].get()
CHAR_MARGIN = CONFIG['epar_downloader']['char_margin'].get(float)


@pytest.mark.parametrize('product', ['test', None])
def test_downloader_raise_error_wrong_product(product, monkeypatch):
    """Test the downloader for the raise of error of wrong product."""

    epar_downloader = EPARDownloader(product)

    def mock_main_url(self):

        check_param('product', product, ['Azarga', 'Evista'])

    monkeypatch.setattr(
        'docomp.content._epar._downloading.EPARDownloader.main_url_',
        property(mock_main_url),
    )

    if not isinstance(product, str):
        with pytest.raises(
            TypeError,
            match=f'Parameter `product` should be a string. '
            f'Got {type(product)} instead.',
        ):
            epar_downloader.main_url_
    else:
        with pytest.raises(ValueError, match='Instead test was given.$'):
            epar_downloader.main_url_


@pytest.mark.parametrize('language', ['test', None])
def test_downloader_raise_error_wrong_language(language, monkeypatch):
    """Test the downloader for the raise of error of wrong product."""

    epar_downloader = EPARDownloader('Evita', language)

    def mock_download_url(self):

        check_param('language', language, ['en', 'fr'])

    monkeypatch.setattr(
        'docomp.content._epar._downloading.EPARDownloader.download_url_',
        property(mock_download_url),
    )

    if not isinstance(language, str):
        with pytest.raises(
            TypeError,
            match=f'Parameter `language` should be a string. '
            f'Got {type(language)} instead.',
        ):
            epar_downloader.download_url_
    else:
        with pytest.raises(ValueError, match='Instead test was given.$'):
            epar_downloader.download_url_


@pytest.mark.parametrize('product,language', PRODUCTS_LANGUAGES)
def test_downloader(product, language, monkeypatch):
    """Test the EPAR downloader class."""

    epar_downloader = EPARDownloader(product, language)

    def mock_download_url(self):
        self.available_languages_ = ['en', 'fr']
        self.language_ = check_param(
            'language', self.language.lower(), self.available_languages_
        )
        return urljoin(BASE_URL, f'{PRODUCT_URL.format(product)}_{language}.pdf')

    def mock_download(self):
        pages = list(
            extract_pages(
                join(DOWNLOADING_PATH, f'{product}_sections_{language}.pdf'),
                laparams=LAParams(boxes_flow=BOXES_FLOW, char_margin=CHAR_MARGIN),
            )
        )
        return pages

    monkeypatch.setattr(
        'docomp.content._epar._downloading.EPARDownloader.download_url_',
        property(mock_download_url),
    )
    monkeypatch.setattr(
        'docomp.content._epar._downloading.EPARDownloader.download', mock_download
    )
    monkeypatch.setattr(
        'docomp.content._epar._downloading.EPARDownloader.REPORT_URL_', REPORT_PATH
    )
    monkeypatch.setattr(
        'docomp.content._epar._downloading.EPARDownloader.SKIPROWS_', None
    )
    monkeypatch.setattr(
        'docomp.content._epar._downloading.EPARDownloader.USECOLS_', None
    )

    epar_downloader.download()
    assert isinstance(epar_downloader.report_, pd.DataFrame)
    assert hasattr(epar_downloader, 'available_products_')
    assert epar_downloader.main_url_ == join(
        BASE_URL, f'{language}/medicines/human/EPAR/{product.lower()}'
    )
