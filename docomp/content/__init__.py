"""
The :mod:`docomp.content` provides the tools to download and extract leaflet
content from the industry and EMA documents.
"""

from ._epar._main import extract_epar_content

__all__ = ['extract_epar_content']
