"""
Includes classes and functions to download the latest EPAR document and extract
data from it.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>

from abc import abstractmethod
from urllib.request import urlretrieve
from functools import cached_property


class BaseDownloader:
    """Base class to download data."""

    @staticmethod
    def _check_param(param_name, param, available_params):
        """Check parameter."""

        # Check type
        if not isinstance(param, str):    
            raise TypeError(
                f'Parameter `{param_name}` should be a string. Got {type(param)} instead.'
            )

        # Check available products
        if param not in available_params:
            raise ValueError(
                f'Parameter `{param_name}` should be one of {", ".join(available_params)}.\n\n'
                f'Instead {param} was given.'
            )

        return param
    
    @cached_property
    def downloaded_data_(self):
        return self.download()
    
    @abstractmethod
    def download(self):
        """Download the data."""
        pass


class BaseExtractor:
    """Base class to extract data."""

    def __init__(self, pages):
        self.pages = pages

    @cached_property
    def extracted_data_(self):
        return ''.join(self.extract())
    
    @abstractmethod
    def extract(self):
        """Extract the data."""
        pass
