"""
Test the _epar module.
"""

import pytest

from docomp.extraction._epar import convert_to_dict


@pytest.mark.parametrize('product', ['test', None])
def test_raise_error_wrong_product(product):
    """Test the error of error for wrong product."""
    if not isinstance(product, str):
        with pytest.raises(
            TypeError,
            match=f'Parameter `product` should be a string. '
            f'Got {type(product)} instead.',
        ):
            convert_to_dict(product)
    else:
        with pytest.raises(ValueError, match='Instead Test was given.$'):
            convert_to_dict(product)


@pytest.mark.parametrize('language', ['test', None])
def test_raise_error_wrong_language(language):
    """Test the error of error for wrong language."""
    if not isinstance(language, str):
        with pytest.raises(
            TypeError,
            match=f'Parameter `language` should be a string. '
            f'Got {type(language)} instead.',
        ):
            convert_to_dict('Evicto', language)
    else:
        with pytest.raises(ValueError, match='Instead test was given.$'):
            convert_to_dict('Evicto', language)


@pytest.mark.parametrize('product,language', [('Azarga', 'en'), ('Evista', 'en')])
def test_extract_labelling_content(product, language):
    """Test the extraction of labelling content."""
    doc_dict = convert_to_dict(product, language)
    assert isinstance(doc_dict, dict)


@pytest.mark.parametrize('product,language', [('Azarga', 'en'), ('Evista', 'en')])
def test_extract_leaflet_content(product, language):
    """Test the extraction of labelling content."""
    doc_dict = convert_to_dict(product, language)
    assert isinstance(doc_dict, dict)
