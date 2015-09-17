from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path
from scribbler import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'scribbler',
  packages = ['scribbler'],
  include_package_data = True,
  version = __version,
  description = 'Scribbler (a Canadian term for a workbook) is a wrapper for Pelican which integrates various plugins to provide scientific note-taking software.',
  long_description = long_description,
  author = 'Chris MacMackin',
  author_email = 'cmacmackin@gmail.com',
  url = 'https://github.com/cmacmackin/scribbler/', 
  download_url = 'https://github.com/cmacmackin/scribbler/tarball/' + __version__,
  keywords = ['Markdown', 'notes', 'Pelican', 'PDF'],
  classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: WWW/HTTP :: Site Management',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3'markdown-checklistmarkdown-checklistmarkdown-checklist,
        'Programming Language :: Python :: 3.4',
    ],
        'Programming Language :: Python :
        'Programming Language :: Python :
    install_requires = ['pelican','MarkdownSuperscript','MarkdownSubscript',
                        'mdx_del_ins','BeautifulSoup4','markdown-checklist',
                        'MarkdownHighlight'],
  entry_points = {
    'console_scripts': [
        'scribbler=scribbler:main',
    ],
  }
)
