"""Tools to extract and compare leaflet and labelling documents of various
drugs for European Medicines Agency.

``docomp`` is a set of tools for leaflet and labelling documents comparison of
various drugs. It provides python functions to download the latest EPAR document
and extract information from it, extract data from the submitted by the industry
leaflet and labelling documents as well as compare them and provide a similarity
measure.

Subpackages
-----------
extraction
    Module which provides the functions to download and extract data.
comparison
    Module which provides the functions to compare the leaflet and labelling documents.
"""

import confuse

from . import extraction
from . import comparison
from ._version import __version__

__all__ = ['extraction', 'comparison', '__version__']

CONFIG = confuse.Configuration('document-comparison', __name__)
