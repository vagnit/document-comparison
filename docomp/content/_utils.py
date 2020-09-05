"""
Includes utilities functions and classes.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>

from abc import abstractmethod
from functools import cached_property


def check_param(param_name, param, available_params):
    """Check parameter type and value."""

    # Check type
    if not isinstance(param, str):
        raise TypeError(
            f'Parameter `{param_name}` should be a string. Got {type(param)} instead.'
        )

    # Check available parameters
    if param not in available_params:
        raise ValueError(
            f'Parameter `{param_name}` should be one of '
            f'{", ".join(available_params)}.\n\nInstead {param} was given.'
        )

    return param


class BaseDownloader:
    """Base class to download data."""

    @cached_property
    def downloaded_data_(self):
        return self.download()

    @abstractmethod
    def download(self):
        """Download the data."""
        pass


class BaseExtractor:
    """Base class to extract data from pdf pages."""

    def __init__(self, pages):
        self.pages = pages

    @cached_property
    def extracted_data_(self):
        return self.extract()

    @abstractmethod
    def extract(self):
        """Extract the data."""
        pass
