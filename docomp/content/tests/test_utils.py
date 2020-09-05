"""
Test the _utils module.
"""

import pytest

from docomp.content._utils import BaseDownloader, BaseExtractor, check_param


class Downloader(BaseDownloader):
    """A downloader class for testing."""

    def __init__(self, data=None, param=None, available_params=None):
        self.data = data
        self.param = param
        self.available_params = available_params

    def download(self):
        if self.available_params is not None:
            self.param_ = check_param('param', self.param, self.available_params)
        return self.data


class Page:
    """A page class for testing."""

    def __init__(self, content):
        self.content = content


class Extractor(BaseExtractor):
    """An extractor class for testing."""

    def extract(self):
        html = ''
        for page in self.pages:
            lines = page.content.splitlines()
            for line in lines:
                if line == 'Title':
                    html += f'<p><b>{line}</b></p>'
                else:
                    html += f'<p>{line}</p>'
        return ''.join(html)


@pytest.mark.parametrize('param', ['test', None])
def test_check_param(param):
    """Test the raise of error for wrong parameter value."""

    available_params = ['param1', 'param2', 'param3']

    if not isinstance(param, str):
        with pytest.raises(
            TypeError,
            match='Parameter `param` should be a string. '
            'Got <class \'NoneType\'> instead.',
        ):
            check_param('param', param, available_params)
    else:
        with pytest.raises(
            ValueError,
            match='Parameter `param` should be one of param1, param2, param3.'
            '\n\nInstead test was given.$',
        ):
            check_param('param', param, available_params)


@pytest.mark.parametrize('data', ['test', None])
def test_base_downloader(data):
    """Test the download method and downloaded data."""
    downloader = Downloader(
        data, 'param1', available_params=['param1', 'param2', 'param3']
    )
    downloader.download()
    assert downloader.param_ == 'param1'
    assert downloader.downloaded_data_ == data


@pytest.mark.parametrize('data', ['test', None])
def test_base_extractor(data):
    """Test the extract method and extracted data."""
    pages = [Page('Title'), Page('Line1\nLine2')]
    extractor = Extractor(pages)
    extractor.extract()
    assert extractor.extracted_data_ == '<p><b>Title</b></p><p>Line1</p><p>Line2</p>'
