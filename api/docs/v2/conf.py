#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Opentrons API documentation build configuration file, created by
# sphinx-quickstart on Thu Oct 27 12:10:26 2016.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import json
import pkgutil

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../sphinxext'))

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.imgmath',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinxext.opengraph',
    'sphinx_tabs.tabs',
    # todo(mm, 2021-09-30): Remove numpydoc when we're done transitioning to
    # Google-style docstrings. github.com/Opentrons/opentrons/issues/7051
    'numpydoc'

]


intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}


# Add any paths that contain templates here, relative to this directory.
templates_path = ['../templates', '../templates/v2']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The encoding of source files.
#
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Python Protocol API v2'
copyright = '2010–23, Opentrons'
author = 'Opentrons Labworks'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# todo(mm, 2021-09-30): Depending on where these show up, would it be more correct
# to use the latest-supported *apiLevel* instead of the *Python package version*?

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
import python_build_utils
sys.path = sys.path[:-1]
_vers = python_build_utils.get_version('api', 'robot-stack')


# The short X.Y version.
version = '.'.join(_vers.split('.')[:2])
# The full version, including alpha/beta/rc tags.
release = _vers

# setup the code block substitution extension to auto-update apiLevel
extensions += ['sphinx-prompt', 'sphinx_substitution_extensions']

# use rst_prolog to hold the subsitution
# update the apiLevel value whenever a new minor version is released
rst_prolog = f"""
.. |apiLevel| replace:: 2.21
.. |release| replace:: {release}
"""

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#
# today = ''
#
# Else, today_fmt is used as the format for a strftime call.
#
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all
# documents.
#
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'murphy'

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'travis_button': False,
    'font_size': '14px',
    'font_family': "'Open Sans', sans-serif",
    'head_font_family': "'AkkoPro-Regular', 'Open Sans'",
    'sidebar_collapse': 'True',
    'fixed_sidebar': 'True',
    'sidebar_width': '270px',
    'github_user': 'opentrons',
    'github_repo': 'opentrons',
    'github_button': True,
    # 'analytics_id': 'UA-83820700-1',
    'description': 'Python Protocol API',
    'link': '#006FFF',
    'link_hover': '#05C1B3',
    'sidebar_list': '#05C1B3',
    'sidebar_link_underscore': '#DDDDDD',
}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.
# "<project> v<release> documentation" by default.
#
html_title = 'Opentrons Python API V2 Documentation'


# A shorter title for the navigation bar.  Default is the same as html_title.
#
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#
# html_logo = '../img/logo.png'

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or
# 32x32 pixels large.
#
html_favicon = '../img/OTfavicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['../static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#
# html_extra_path = []

# If not None, a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# The empty string is equivalent to '%b %d, %Y'.
#
# html_last_updated_fmt = None

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# Use separate sidebar nav overrides to force (for apiv2) or ignore

# (apiv1) the apiv2 hidden toctree elements (our sphinx overrides css
# forces the body toctrees hidden using css)
html_sidebars = {
    '*': [
        'about.html',
        'toc-with-nav.html',
        'relations.html',
        'searchbox.html'
    ]
}


# Additional templates that should be rendered to pages, maps page names to
# template names.
#
# html_additional_pages = {'index': 'v2/index.html'}

# If false, no module index is generated.
#
# html_domain_indices = True

# If false, no index is generated.
#
# html_use_index = True

# If true, the index is split into individual pages for each letter.
#
# html_split_index = False

# If true, links to the reST sources are added to the pages.
#
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'h', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'r', 'sv', 'tr', 'zh'
#
# html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# 'ja' uses this config value.
# 'zh' user can custom change `jieba` dictionary path.
#
# html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
#
# html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = 'OpentronsAPIV2doc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
     # The paper size ('letterpaper' or 'a4paper').
     #
     # 'papersize': 'letterpaper',

     # The font size ('10pt', '11pt' or '12pt').
     #
     # 'pointsize': '10pt',
     # Additional stuff for the LaTeX preamble.
     #
     # 'preamble': r'\setlistdepth{15}',

     # Enable Greek symbol encoding for our sweet mus
     #
     'fontenc': r'\usepackage[LGR,T1]{fontenc}',

     # Latex figure (float) alignment
     #
     'figure_align': 'H',
    'maxlistdepth': '10',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'OpentronsPythonAPIV2.tex',
     'Opentrons Python API V2 Documentation',
     'Opentrons Labworks', 'howto'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#
latex_logo = '../img/logo.png'

#latex_toplevel_sectioning = 'section'

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#
# latex_use_parts = False

# If true, show page references after internal links.
#
latex_show_pagerefs = True

# If true, show URL addresses after external links.
#
latex_show_urls = 'footnote'

# Documents to append as an appendix to all manuals.
#
# latex_appendices = []

# It false, will not define \strong, \code, 	itleref, \crossref ... but only
# \sphinxstrong, ..., \sphinxtitleref, ... To help avoid clash with user added
# packages.
#
# latex_keep_old_macro_names = True

# If false, no module index is generated.
#
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = []

# If true, show URL addresses after external links.
#
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = []

numpydoc_show_class_members = False

# TODO: fix invalid :any: references
suppress_warnings = []

# Documents to append as an appendix to all manuals.
#
# texinfo_appendices = []

# If false, no module index is generated.
#
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#
# texinfo_no_detailmenu = False

# -- Options for Opengraph tags -------------------------------------------

ogp_site_url = "https://docs.opentrons.com/v2/"
ogp_site_name = "Opentrons Python Protocol API"
ogp_image = "_static/PythonAPI.png"
ogp_description_length = 170
ogp_enable_meta_description = False

# -- Options for tabs -----------------------------------------------------

sphinx_tabs_disable_tab_closing = True

# -- Suppress autodoc warnings --------------------------------------------

# Ignore warnings for deliberately missing/undocumented things that appear
# in automatically generated type signatures.
#
# The goal here is to pass through any warnings for bad targets of MANUALLY
# created links.
nitpick_ignore_regex = [
    ("py:class", r".*Optional\[.*"),  # any Optional with bad members
    ("py:class", r".*commands\.types.*"),
    ("py:class", r".*hardware_control.*"),
    ("py:class", r".*legacy_broker.*"),
    ("py:class", r".*protocol_api\.core.*"),
    ("py:class", r".*api_support.*"),
    ("py:class", r".*duration\.estimator.*"),
    ("py:class", r".*protocols\.types.*"),
    ("py:class", r".*protocol_api\.deck.*"),
    ("py:class", r".*protocol_api\.config.*"),
    ("py:class", r".*opentrons_shared_data.*"),
    ("py:class", r".*protocol_api._parameters.Parameters.*"),
	("py:class", r".*RobotContext"),  # shh it's a secret (for now)
    ("py:class", r'.*AbstractLabware|APIVersion|LabwareLike|LoadedCoreMap|ModuleTypes|NoneType|OffDeckType|ProtocolCore|WellCore'),  # laundry list of not fully qualified things
]
