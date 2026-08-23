import os
import sys

# Add 'src' and 'bin' folders to Python path (relative to docs/source)
sys.path.insert(0, os.path.abspath("../../src"))
sys.path.insert(0, os.path.abspath("../../bin"))

project = "SVALint"
copyright = "2026, AsFigo, UK"
author = "Srinivasan Venkataramanan, Ajeetha Kumari Venkatesan"

extensions = [
    "myst_parser",  # Allows mixing Markdown (.md) and reST (.rst)
]

# Theme settings
html_theme = "furo"
html_title = "SVALint Documentation"
html_js_files = ["new_tab_links.js"]
