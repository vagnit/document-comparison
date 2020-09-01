"""
Test the _epar module.
"""

from os.path import join

import pytest

from docomp.extraction._epar import extract_epar_content

EPAR_RESOURCES_PATH = join(
    'docomp', 'extraction', 'tests', 'resources', 'epar', '{}_{}.pdf'
)


@pytest.mark.parametrize('product', ['test', None])
def test_raise_error_wrong_product(product, monkeypatch):
    """Test the error of error for wrong product."""

    def mock_extract_product_url(product):
        if product is None:
            raise TypeError(
                'Parameter `product` should be a string. '
                'Got <class \'NoneType\'> instead.'
            )
        elif product == 'test':
            raise ValueError('Instead Test was given.')

    monkeypatch.setattr(
        'docomp.extraction._epar._extract_product_url', mock_extract_product_url
    )

    if not isinstance(product, str):
        with pytest.raises(
            TypeError,
            match=f'Parameter `product` should be a string. '
            f'Got {type(product)} instead.',
        ):
            extract_epar_content(product)
    else:
        with pytest.raises(ValueError, match='Instead Test was given.$'):
            extract_epar_content(product)


@pytest.mark.parametrize('language', ['test', None])
def test_raise_error_wrong_language(language, monkeypatch):
    """Test the error of error for wrong language."""

    def mock_extract_product_language_url(product, language):
        if language is None:
            raise TypeError(
                'Parameter `language` should be a string. '
                'Got <class \'NoneType\'> instead.'
            )
        elif language == 'test':
            raise ValueError('Instead test was given.')

    monkeypatch.setattr(
        'docomp.extraction._epar._extract_product_language_url',
        mock_extract_product_language_url,
    )

    if not isinstance(language, str):
        with pytest.raises(
            TypeError,
            match=f'Parameter `language` should be a string. '
            f'Got {type(language)} instead.',
        ):
            extract_epar_content('Evicto', language)
    else:
        with pytest.raises(ValueError, match='Instead test was given.$'):
            extract_epar_content('Evicto', language)


@pytest.mark.parametrize('product,language', [('Azarga', 'en'), ('Evista', 'en')])
def test_extract_labelling_content(product, language, monkeypatch):
    """Test the extraction of labelling content."""

    path = EPAR_RESOURCES_PATH.format(product.lower(), language)
    monkeypatch.setattr(
        'docomp.extraction._epar._extract_product_language_url',
        lambda product, language: path,
    )
    monkeypatch.setattr('docomp.extraction._epar.urlretrieve', lambda url: (url, None))

    doc_dict = extract_epar_content(product, language)
    assert isinstance(doc_dict, dict)


@pytest.mark.parametrize('product,language', [('Azarga', 'en'), ('Evista', 'en')])
def test_extract_leaflet_content(product, language, monkeypatch):
    """Test the extraction of labelling content."""

    path = EPAR_RESOURCES_PATH.format(product.lower(), language)
    monkeypatch.setattr(
        'docomp.extraction._epar._extract_product_language_url',
        lambda product, language: path,
    )
    monkeypatch.setattr('docomp.extraction._epar.urlretrieve', lambda url: (url, None))

    doc_dict = extract_epar_content(product, language)
    assert isinstance(doc_dict, dict)
