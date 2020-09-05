"""
Includes classes and functions to extract content from the EPAR document.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>

from re import match, split

import pandas as pd
from pdfminer.layout import LTTextContainer, LTFigure

from .._utils import BaseExtractor
from ... import CONFIG

CONFIG = CONFIG['content']['epar']['extraction']['labelling_extractor']
TYPES_MAPPING = {'text': LTTextContainer, 'image': LTFigure}


class EPARBaseExtractor(BaseExtractor):
    """Base class to extract content from EPAR pdf."""

    ELEMENT_TYPE_ = None

    def _extract(self):
        """Extract content."""

        content = []

        # Iterate through pages
        for page in self.pages:

            # Iterate through page elements
            for element in page:

                if isinstance(element, TYPES_MAPPING[self.ELEMENT_TYPE_]):

                    # Iterate through parts of elements
                    for part in element:
                        content.append((page, element, part))

        return content


class SectionExtractor(EPARBaseExtractor):
    """Class to extract the labelling and leaflet sections from EPAR pdf
    document."""

    ELEMENT_TYPE_ = 'text'

    def extract(self):
        """Extract leaflet and labelling sections."""

        content = super(SectionExtractor, self)._extract()

        # Extract pages numbers and lines
        lines = []
        for page, _, part in content:
            line = ' '.join(part.get_text().split())
            if line and str(page.pageid) != line:
                lines.append((page.pageid, line))

        # Number of lines per page
        pages_num_lines = pd.DataFrame(lines).groupby(0).size()

        # Identify sections
        first_num, second_num = self.sections_nums_ = pages_num_lines[
            pages_num_lines == 1
        ].index.tolist()

        # Sections
        sections = self.pages[first_num: (second_num - 1)], self.pages[second_num:]

        return sections


class LabellingHTMLExtractor(EPARBaseExtractor):
    """Class to extract HTML from the labelling section of EPAR."""

    ELEMENT_TYPE_ = 'text'

    @staticmethod
    def _extract_subsections(content):
        """Extract subsections from initial content."""
        sections = ''.join([part.get_text() for *_, part in content]).split('\n \n \n')
        subsections = [section.split('\n \n') for section in sections]
        return subsections

    @staticmethod
    def _split_subsections(subsections):
        """Split subsections to identify them correctly."""
        modified_subsections = []

        # Split on page numbers
        for subsection in subsections:
            for line in split(r'\d+ \|', '|'.join(subsection)):
                modified_subsections.append(line.split('|'))

        # Split on internal enumerated titles
        for index, subsection in enumerate(modified_subsections):
            for line_index, line in enumerate(subsection):
                if match(r'\d+\. ', line) and line_index > 0:
                    modified_subsections.remove(subsection)
                    modified_subsections.insert(index, subsection[:line_index])
                    modified_subsections.insert(index + 1, subsection[line_index:])

        return modified_subsections

    @staticmethod
    def _strip_subsections(subsections):
        """Exclude empty characters and pages numbers."""
        stripped_subsections = []
        for subsection in subsections:
            stripped_subsection = []
            for line in subsection:
                if line and not line.strip().isdigit():
                    stripped_subsection.append(line)
            if stripped_subsection:
                stripped_subsections.append(stripped_subsection)
        return stripped_subsections

    @staticmethod
    def _extract_element(line, bold=True):
        """Extract HTML element from line."""
        line = " ".join(line.split())
        return f'<p><b>{line}</b></p>' if bold else f'<p>{line}</p>'

    def extract(self):
        """Extract HTML elements."""

        # Extract content
        content = super(LabellingHTMLExtractor, self)._extract()

        # Extract and modify subsections
        subsections = self._extract_subsections(content)
        subsections = self._split_subsections(subsections)
        subsections = self._strip_subsections(subsections)

        # Extract html elements
        html_elements = []
        for subsection in subsections:
            first_line, *other_lines = subsection

            # Main title
            if not match(r'\d+\.*', first_line):
                for line in subsection:
                    html_elements.append(self._extract_element(line))

            # Enumerated title
            else:
                html_elements.append(self._extract_element(first_line))
                for line in other_lines:
                    line = line.replace(', \n', ', ').splitlines()
                    for splitted_line in line:
                        html_elements.append(
                            self._extract_element(splitted_line, False)
                        )

        return ''.join(html_elements)


class LeafletHTMLExtractor(EPARBaseExtractor):
    """Class to extract HTML from the leaflet section of EPAR."""

    ELEMENT_TYPE_ = 'text'


class ImagesExtractor(EPARBaseExtractor):
    """Class to extract images from pdf pages."""

    ELEMENT_TYPE_ = 'image'

    def extract(self):

        content = super(ImagesExtractor, self)._extract()

        # Iterate through pages
        images = []
        for *_, part in content:
            images.append(part.stream.get_data())

        return images
