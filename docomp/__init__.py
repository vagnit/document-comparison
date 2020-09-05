"""Tools to extract and compare leaflet and labelling sections of documents
for various drugs.

``docomp`` provides python functions to download the latest EPAR document
and extract information from it, extract data from the submitted by the industry
leaflet and labelling documents as well as compare them and provide a similarity
measure.

Subpackages
-----------
content
    Module which provides the functions and classes to download and extract data.
comparison
    Module which provides the functions and classes to compare the documents.
"""

import confuse

from ._version import __version__

__all__ = ['__version__']

CONFIG = confuse.Configuration('document-comparison', __name__)
