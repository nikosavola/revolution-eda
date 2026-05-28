# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add the project root to the path so Sphinx can find the modules
sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------

project = "Revolution EDA"
copyright = "2024, Revolution Semiconductor"
author = "Revolution Semiconductor"
release = "0.8.11"  # Keep in sync with pyproject.toml [tool.poetry] version

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# Autosummary generates stub pages for API docs
autosummary_generate = True

# MyST parser for Markdown support
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Intersphinx mapping -----------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Autodoc settings --------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}

# Mock imports for modules that may not be available during doc build
autodoc_mock_imports = [
    "PySide6",
    "numpy",
    "gdstk",
    "quantiphy",
    "polars",
    "orjson",
    "anthropic",
    "google",
    "google.generativeai",
    "cryptography",
    "lxml",
    "markdown",
    "pyqtgraph",
]
