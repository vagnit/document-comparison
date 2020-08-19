===================
document-comparison
===================

document-comparison is a set of tools for leaflet and labelling documents
comparison of various drugs. It provides python functions to download the latest
EPAR document and extract information from it, extract data from the submitted
by the industry leaflet and labelling documents as well as compare them and
provide a similarity measure.

Dependencies
------------

document-comparison is tested to work under Python 3.7+. The dependencies are the
following:

- ...(>=...)
- ...(>=...)
...

Installation
------------

Use the following commands to get a copy from GitHub and install all dependencies::

  git clone https://github.com/georgedouzas/document-comparison.git
  cd document-comparison
  pip install .

Or install using pip and GitHub::

  pip install -U git+https://github.com/georgedouzas/document-comparison.git

Testing
-------

After installation, you can use `pytest` to run the test suite::

  make test
