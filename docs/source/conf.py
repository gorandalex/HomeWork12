import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(Path(__file__).parent.parent.parent))
project = 'Rest API'
copyright = '2023, Horobets'
author = 'Horobets'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']