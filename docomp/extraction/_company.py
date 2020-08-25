"""
Includes classes and functions to extract data from
the company's leaflet and label
"""

# Author: Evangelos Nittis <vagos333@gmail.com>
# Author: Georgios Douzas <gdouzas@icloud.com>

from re import sub

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTFigure, LAParams


def _extract_leaflet_content(leaflet_pages):
    """Extract content from the company leaflet document."""

    content = {'text': [], 'images': []}

    # Iterate through pages
    for page in leaflet_pages:

        # Iterate through page elements
        for element in page:

            if isinstance(element, LTTextContainer):

                # # Iterate through lines of elements
                for text_line in element:
                    text = sub(r'\d.\s', '', text_line.get_text().splitlines()[0])
                    if not text.isnumeric():
                        content['text'].append(text)

            elif isinstance(element, LTFigure):
                for img in element:
                    content['images'].append(img.stream.get_data())

    return content


def _leaflet_to_dict_comp(path_to_file):
    """Preparation of the dictionary of the company leaflet
    including keys and values"""

    dict_leaf_comp_in = dict()
    with open(path_to_file) as inputs:
        for line in inputs:
            if line.startswith("<b>"):
                key = line.strip()[3:]
                dict_leaf_comp_in.setdefault(key, list())
            else:
                dict_leaf_comp_in[key].append(line.strip())

    # Merge
    dict_leaf_comp = dict()
    for key, vlist in dict_leaf_comp_in.items():
        dict_leaf_comp[key] = " ".join(vlist)

    return dict_leaf_comp


def convert_to_dict_comp(path):
    """Convert the company leaflet document
    to a dictionary representation."""

    # Extract pdf pages
    leafleat_pages = list(
        extract_pages(path, laparams=LAParams(line_margin=5.0))
    )

    # Extract content
    doc_dict_comp = {
        # label to be added
        'leafleat': _extract_leaflet_content(leafleat_pages),
    }

    return doc_dict_comp
