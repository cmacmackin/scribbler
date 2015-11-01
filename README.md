# Scribbler
Scribbler is a piece of software for managing a notebook from the command line.
It was written with scientific note-taking in mind, but could be used for other
purposes as well.

## Motivation
In my graduate studies in physics, much of my research tends to be
computational. I have never been able to stomach the idea of copying output
from a script off of the screen into a physical notebook when it would be
so much easier just to copy and paste it into a digital notebook. Furthermore,
while a hard copy notebook is very convenient for sketching graphs, it can be
a pain to have to print a copy of any graphs you produce on the computer if you
want to include theme, and even more of a pain gluing or stapling them onto
the page.

However, I have found that many of the electronic note-keeping software to be
little better. Most of my graphs tend to be saved as PDF files, which can't be
added as an image to the notes. Adding links, equations, table, and figures
often requires a cumbersome series of button-clicks. Furthermore, including
an image usually only provides a link to the image's location on the computer,
which will cause problems if I later delete or move it. To avoid this problem
I could copy all such images to a notebook location, but at this point the
convenience of keeping notes on the computer is starting to decay. Lastly,
while it is convenient to take notes on your computer if you are taking them
about work done on the computer, there will always be times that work has to
be done on paper. How to include that with the digital notes? Scanning would
work but is a tedious, inconvenient process.

Out of this frustration, Scribbler was born. The goal was to
allow notes to be taken in Markdown, avoiding the need for irritating button
pressing when links and images need to be added, with sufficient extensions
to make the inclusion of PDF images, LaTeX, BibTeX-style referencing, and
various other features possible. Scribbler achieves this by acting as a wrapper
for the [Pelican](https://github.com/getpelican/pelican) static-site generator,
for which various additional plugins have been written to give it the
desired features. Scribbler also converts the HTML output of Pelican into
PDF files which can be printed and placed in a binder along with any
hand-written notes.

## What's in a name?
"Scribbler" is a Canadian term (less-used now) for a school-child's notebook
or workbook. Canadians will likely remember ones such as these from their
elementary school days:
![Hilroy notebooks, or "scribblers."](https://raw.githubusercontent.com/cmacmackin/scribbler/master/hilroy-scribbler.png)

## Installation
Scribbler is not yet available on PyPI. However, the following process can be
used to handle all Python dependencies:

```
git clone https://github.com/cmacmackin/scribbler.git
cd scribbler
./install-wkhtmltopdf.sh #Or can install form package manager (see below)
sudo apt-get install libmagickwand-dev python-dev  #If using Ubuntu or Debian
pip install .
```

Note that the version of [wkhtmltopdf](http://wkhtmltopdf.org/) on Debian and
Ubuntu-based Linux distributions has not been compiled with certain patches
needed to provide full functionality. Most of this functionality is not
important for Scribbler, except in two areas:

1. The inclusion of any links from the HTML in the PDF.
2. Without the patched version, the text in the output is very small and
   difficult to read.

For this reason, it is reccomended that you install a patched binary using
the `install-wkhtmltopdf.sh` script provided.

## Basic Use
Scribbler manages a set of _notebooks_. You can create a notebook with
```
scribbler init NAME LOCATION
```
This will cause Scribbler to add to its records a notebook with the title
"NAME" and create the notebook directory hierarchy at "LOCATION". If a notebook
hierarchy already exists there then Scribbler will attempt to use it. The
notebook hierarchy is as follows:
```
notebook-directory
├── appendices   # Files containing appendices to your notebook
├── files        # Images, PDFs, etc. which you wish to include in the notebook
│   ├── ...      # The exact subdirectory structure depends on the notebook's configurations
│   └── ...
├── html         # HTML output of the notebook
├── notebook.yml # A YAML file specifying the notebook's settings
├── notes        # Files containing individual notes
└── pdf          # PDF output of the notebook
```

To see all notebooks known to scribbler, run
```
scribbler notebooks
```
In order to modify a notebook, it must be loaded into Scribbler. To do this
run
```
scribbler load NAME
```
Notebooks can be unloaded with
```
scribbler unload
```
Any time `scribbler load`
is run, any previously loaded notebooks will automatically be unloaded.

The settings for the notebook can be edited using
```
scribbler settings
```
To create a new note, run
```
scribbler new -t 'Note Title'
```
which will create a note for today's date with the specified title and will
open it in the system's text editor. Once you are done writing the note
(see next section), save it and close the text editor. A list of all notes
(as well as information about the notebook) can be printed with the command
```
scribbler list
```
To produce the HTML and PDF versions of the notebook, simply run
```
scribbler build
```
Each PDF that is rendered will pause for 2.5 seconds in order to ensure that
any math included in the note has sufficient time to be rendered by
[MathJax](https://www.mathjax.org/). In order to avoid this time-penalty,
PDFs will only be generated if no PDF exists already, or the note source
file has been edited more recently than the existing PDF.

These commands can be run from any directory. This means that if you are
in the process of compiling some software and suddenly realise you want to
takes some notes about it, you can easily do so without having to navigate
away from the compilation directory or open a new terminal.

You can also add appendices. These are like notes, except that they don't
have any date associated with them and will always be placed at the end of the
notebook. They are created using almost exactly the same syntax as for notes:
```
scribbler new --appendix -t 'Note Title'
```

If you need to edit the note later, run
```
scribbler src --title 'Note Title'
```
You can view the HTML version of that note with
```
scribbler html --title 'Note Title'
```
and the PDF version with
```
scribbler pdf --title 'Note Title'
```
Adding files to the notebook manually is possible but is not recommended,
as Scribbler will not know the date or title and therefore will not be able
to use the `src`, `html`, or `pdf` commands to open them.

## Writing Notes
By default notes are written in
[Markdown](https://daringfireball.net/projects/markdown/), although they may
also be written in [reStructuredText](http://docutils.sourceforge.net/rst.html)
or HTML. As Scribbler is just a wrapper for Pelican, it is strongly recommended
that you read its documentation on
[writing content](http://docs.getpelican.com/en/3.6.3/content.html). Note that
what they refer to as "articles" are equivalent to notes and what they refer
to as "pages" are equivalent to appendices. The Pelican syntax for internal
links _will_ work with Scribbler, although Scribbler's directory structure
is a little different. Whereas the root of the directory structure seen by
Pelican is the `content` directory, for Scribbler it is the top level of the
notebook's directory. However, links will only be generated to the contents of
the `notes`, `appendices`, and `files` folders.

### Markdown Extensions
In addition to standard Markdown, various plugins are loaded providing
extra functionality. Of particular note is 
[Markdown Extra](https://pythonhosted.org/Markdown/extensions/extra.html),
which provides syntax for such things as footnotes, tables, and more.
[CodeHilite](https://pythonhosted.org/Markdown/extensions/code_hilite.html)
provides syntax-highlighting for code-snippets, as described in the
Pelican documentation.
[figureAltCaption](https://github.com/jdittrich/figureAltCaption) will convert
each image which stands in its own paragraph into a `<figure>` element, with
the alt-text used as a caption. Other extra pieces of syntax which various
plugins support is:

- text between `^` characters will appear as superscript
  ([MarkdownSuperscript](https://pypi.python.org/pypi/MarkdownSuperscript))
- text between `~` characters will appear as subscript
  ([MarkdownSubscript](https://pypi.python.org/pypi/MarkdownSuperscript))
- Text between `++` markes will be placed in `<ins>` tags, while text between
  `~~` markers will be placed in `<del>` tags. 
  ([mdx_del_ins](https://github.com/aleray/mdx_del_ins))
- Placing `[ ]` at the start of a list-item in an unordered list will render
  an empty checkbox, while `[x]` will render a ticked checkbox (as in
  [GitHub flavoured markdown](https://github.com/blog/1375-task-lists-in-gfm-issues-pulls-comments))
  ([markdown_checklist](https://github.com/FND/markdown-checklist))
- Text between `???` markers will be placed between `<mark>` tags
  ([MarkdownHighlight](https://github.com/ribalba/markdown.highlight))
- Text of the form `{! filepath !}` will be replaced by the contents of the
  file located at `filepath`. Note that, at the moment, this will only work
  when absolute paths are provided.
  ([markdown_include](https://pypi.python.org/pypi/markdown-include))

### Pelican Extensions
Additionally, several Pelican plugins are used to provide further
functionality. These plugins can be used with reStructuredText and HTML content
as well as Markdown.

[render_math](https://github.com/getpelican/pelican-plugins/tree/master/render_math) provides support for LaTeX equations. In Markdown, inline math
appears between dollar signs. However, there must be now white spacce before the
ending `$` (i.e. `$x^2$` will render, but `$ x^2 $` will not). Math appearing on
its own line should use double dollar-signs (`$$`). `\begin{equation}` and
`\end{equation}` can also be used and the equation can be labelled and
referenced, as in actual LaTeX. Note that this depends on
[MathJax](https://www.mathjax.org/) to work and will only render if there is
an internet connection.

The [pdf-img](https://github.com/cmacmackin/pdf-img) plugin, which I wrote
specifically for Scribbler, allows PDF, PS, and EPS graphics to be used
as the source for images. This plugin will simply scan through all images
in each note and appendix. If it ends with the extension `pdf`, `ps`, or `eps`
then it will create a PNG thumbnail of the first page of the document. This
thumbnail will be inserted as the image source, while the image itself will
act as a link to the original PDF/PS/EPS file.

My [figure-ref](https://github.com/cmacmackin/figure-ref) plugin (also written
for Scribbler) will look for any figures in the HTML output whose caption
begins with the format `labelname :: `. This will be replaced by a figure
number. Any references to `{#labelname}` in the rest of the note will also
be replaced with the correct figure number.

Finally, [pelican-cite](https://github.com/cmacmackin/pelican-cite) allows
BibTeX-style referencing within your notes. If a `bibfile` is specified in
your notebook settings then it will be used as a database of bibliographic
data. This file may, optionally be provided or overridden on a per-note
basis by adding the metadata `publications_src`. Inline references can then
be provided with the syntax `[@bibtexkey]` (for author names with year in
parentheses) or `[@@bibtexkey]` (for author names and year all in parentheses).
The inline citation will act as a link to a full bibliography entry at the end
of the note.

## notebook.yml
Settings for your notebook are stored in a file called "notebook.yml" at the
root of your notebook directory. Scribbler can open this for you using the
command `scribbler settings`. This file contains [YAML](http://yaml.org/)
and the following specifications can be set:

- __author__: name of the author of the notebook (_Default:_ "No Author")
- __notebook name__: the name of your notebook to appear in the output. Note
  that this is distinct by the name which Scribbler uses to identify your
  notebook from the command line. (_Default:_ "A Scribbler Notebook")
- __timezone__: the timezone which will be used for dates (_Default:_ "Etc/UCT")
- __language__: the language notes will be written in (_Default:_ "en")
- __links__: a list of links to appear in the sidebar of the HTML notebook.
  Each link should be a two-item list where the first item is the text to
  display in the link and the second item is the URL.
- __email__: the author's email address
- __description__: a description of the notebook. This should be formatted in
  HTML.
- __address__: whether to display the author's address information in the output
  (_Default:_ False)
- __street address__: the author's street address
- __city__: the author's city
- __region__: the author's region (e.g. state or province)
- __postal__: the author's postal or zip code
- __country__: the author's country
- __plugins__: a list of any additional
  [Pelican plugins](https://github.com/getpelican/pelican-plugins) which
  the author wants to be used. These must be located somewhere in the Python
  path.
  [render_math](https://github.com/getpelican/pelican-plugins/tree/master/render_math),
  [tipue_search](https://github.com/getpelican/pelican-plugins/tree/master/tipue_search),
  [neighbours](https://github.com/getpelican/pelican-plugins/tree/master/neighbors),
  [pdf-img](https://github.com/cmacmackin/pdf-img),
  [slugcollision](https://github.com/leofiore/pelican-plugins/tree/master/slugcollision),
  [pelican-cite](https://github.com/cmacmackin/pelican-cite),
  and [figure-ref](https://github.com/cmacmackin/figure-ref) will always be
  loaded. Note that the versions of render\_math and tipue\_search used by
  Scribbler have been slightly modified from the originals.
- __markdown extensions__: a list of any additional
  [Markdown extensions](https://pythonhosted.org/Markdown/extensions/) to be
  used. These must be located in the Python path. The
  [Markdown Extra](https://pythonhosted.org/Markdown/extensions/extra.html),
  [CodeHilite](https://pythonhosted.org/Markdown/extensions/code_hilite.html),
  [figureAltCaption](https://github.com/jdittrich/figureAltCaption),
  [MarkdownSuperscript](https://pypi.python.org/pypi/MarkdownSuperscript),
  [MarkdownSubscript](https://pypi.python.org/pypi/MarkdownSuperscript),
  [mdx_del_ins](https://github.com/aleray/mdx_del_ins),
  [markdown_checklist](https://github.com/FND/markdown-checklist),
  [MarkdownHighlight](https://github.com/ribalba/markdown.highlight),
  and [markdown_include](https://pypi.python.org/pypi/markdown-include)
  extensions will always be loaded.
- __bibfile__: a BibTeX file whose contents will be made available to cite
  (see [pelican-cite](https://github.com/cmacmackin/pelican-cite))
- __filetypes__: a mapping describing where files with various extensions
  which Scribbler copies or links into the notebook will be placed. The entry
  '\*' designates the location for any files with unmatched extensions. If this
  is set in the YAML file then it will not automatically override the default
  settings for all extensions--only those which are explicitly set in the YAML
  file. (_Default:_ {'jpg': 'images', 'jpeg': 'images', 'png': 'images',
  'gif': 'images', 'eps': 'images', 'svg': 'images', 'pdf': 'pdfs',
  'ps': 'pdfs', 'dvi': 'pdfs', 'tar.gz': 'archives', 'tar.bz': 'archives',
  'tar.bz2': 'archives', 'tar.xz': 'archives', 'tar': 'archives',
  'rar': 'archives', 'zip': 'archives', 'rtp': 'archives', 'deb': 'archives',
  '*': 'attachments'})
- __paper__: the paper size to use for PDF output (_Default:_ "Letter")

## Command Line Interface
Scribbler has the following CLI:

    Usage: scribbler [OPTIONS] COMMAND [ARGS]...
    
    Options:
      --version  Show the version and exit.
      --help     Show this message and exit.
    
    Commands:
      add        Registers an existing file at PATH as a note...
      build      Creates the HTML and PDF output of the...
      cd         Launches the currently loaded notebook's...
      copy       Copies SRC to the appropriate location within...
      forget     Remove notebook NAME from Scribbler's...
      html       Opens the HTML file(s) for note(s) with date...
      init       Create a new notebook with NAME.
      link       Creates a hard link to SRC in the files...
      list       Lists the contents of the currently loaded...
      load       Load notebook NAME, meaning that Scribbler...
      new        Creates a new note or appendix in the...
      notebooks  Lists all notebooks known to Scribbler.
      pdf        Opens the PDF file(s) for note(s) with date...
      settings   Opens the YAML file containing the notebook's...
      src        Opens the source file(s) for note(s) with...
      symlink    Creates a symlink to SRC.
      unload     Unload the currently loaded notebook from...

The interface for each command is given in the following sections.

### add
    Usage: scribbler add [OPTIONS] PATH

      Registers an existing file at PATH as a note or appendix.
    
    Options:
      -t, --title TEXT              Title of the note/appendix. Default: current
                                    day of week.
      -d, --date TEXT               Date to use for the new note, in format "YYYY-
                                    MM-DD HH:mm". Default: today's date.
      --overwrite / --no-overwrite  Overwrite an existing record for this file.
                                    Default: no-overwrite.
      --note / --appendix           Whether to create a note or an appendix.
                                    Default: note.
      --help                        Show this message and exit.

### build
    Usage: scribbler build [OPTIONS]
    
      Creates the HTML and PDF output of the currently loaded notebook.
    
    Options:
      --help  Show this message and exit.

### cd
    Usage: scribbler cd [OPTIONS]
    
      Launches the currently loaded notebook's directory in a file browser.
    
    Options:
      --help  Show this message and exit.

### copy
    Usage: scribbler copy [OPTIONS] SRC
    
      Copies SRC to the appropriate location within the files directory of your
      notebook. Unless the `-d/--destination` flag is used, files will be placed
      in the directory corresponding to their file type, as specified in the
      notebook's YAML file.
    
    Options:
      -d, --destination PATH  Destination, relative to the root of the notebook
                              files directory, to which SRC is copied.
      -R, --recursive         Copy the contents of directories recursively. If a
                              destination is specified then the directory tree
                              will be reproduced there. Otherwise, the individual
                              files will be placed in the default location for
                              their filetype.
      -f, --force             Overwrite files without asking permission first.
      --help                  Show this message and exit.

### forget
    Usage: scribbler forget [OPTIONS] NAME
    
      Remove notebook NAME from Scribbler's records.
    
    Options:
      --yes                   Are you sure you want to forget this notebook?
      --delete / --no-delete  Delete the contents of the notebook. Default: no-
                              delete
      --help                  Show this message and exit.

### html
    Usage: scribbler html [OPTIONS] IDENT
    
      Opens the HTML file(s) for note(s) with date or title corresponding to
      IDENT. If HTML version does not exist, then will build it.
    
    Options:
      --date / --title     Whether IDENT is the date or title to search for.
                           Default: date.
      --note / --appendix  Whether searches for a note or an appendix matching
                           IDENT. Default: note.
      --help               Show this message and exit.

### init
    Usage: scribbler init [OPTIONS] NAME LOCATION
    
      Create a new notebook with NAME. If a notebook already exists in LOCATION
      then it will be scanned for information. Otherwise, Scribbler will create
      the necessary files.
    
    Options:
      --help  Show this message and exit.

### link
    Usage: scribbler link [OPTIONS] SRC
    
      Creates a hard link to SRC in the files directory of your notebook. Unless
      the `-d/--destination` flag is used, links will be placed in the directory
      corresponding to their file type, as specified in the notebook's YAML
      file.
    
    Options:
      -d, --destination PATH  Destination, relative to the root of the notebook
                              files directory, for the link to be placed.
      -R, -r, --recursive     Link the contents of directories recursively. If a
                              destination is specified then the directory tree
                              will be reproduced there. Otherwise, the individual
                              links will be placed in the default location for
                              their filetype.
      -f, --force             Overwrite files without asking permission first.
      --help                  Show this message and exit.

### list
    Usage: scribbler list [OPTIONS]
    
      Lists the contents of the currently loaded notebook.
    
    Options:
      --help  Show this message and exit.

### load
    Usage: scribbler load [OPTIONS] NAME
    
      Load notebook NAME, meaning that Scribbler operations will act on it.
    
    Options:
      --help  Show this message and exit.

### new
    Usage: scribbler new [OPTIONS]
    
      Creates a new note or appendix in the currently loaded notebook.
    
    Options:
      -d, --date TEXT             Date to use for the new note, in format "YYYY-
                                  MM-DD HH:mm". Default: today's date.
      -t, --title TEXT            Title of the new note/appendix. Default: current
                                  day of week.
      -m, --markup [md|rst|html]  Markup format to use for the note. Default: md.
      --note / --appendix         Whether to create a note or an appendix.
                                  Default: note.
      --help                      Show this message and exit.

### notebooks
    Usage: scribbler notebooks [OPTIONS]
    
      Lists all notebooks known to Scribbler.
    
    Options:
      --help  Show this message and exit.

### pdf
    Usage: scribbler pdf [OPTIONS] IDENT
    
      Opens the PDF file(s) for note(s) with date or title corresponding to
      IDENT.
    
    Options:
      --date / --title     Whether IDENT is the date or title to search for.
                           Default: date.
      --note / --appendix  Whether searches for a note or an appendix matching
                           IDENT. Default: note.
      --help               Show this message and exit.

### settings
    Usage: scribbler settings [OPTIONS]
    
      Opens the YAML file containing the notebook's settings.
    
    Options:
      --help  Show this message and exit.

### src
    Usage: scribbler src [OPTIONS] IDENT
    
      Opens the source file(s) for note(s) with date or title corresponding to
      IDENT.
    
    Options:
      --date / --title     Whether IDENT is the date or title to search for.
                           Default: date.
      --note / --appendix  Whether searches for a note or an appendix matching
                           IDENT. Default: note.
      --help               Show this message and exit.

### symlink
    Usage: scribbler symlink [OPTIONS] SRC
    
      Creates a symlink to SRC. Unless the `-d/--destination`  flag is used,
      links will be placed in the directory corresponding to their file type, as
      specified in the notebook's YAML file.
    
    Options:
      -d, --destination PATH  Destination, relative to the root of the notebook
                              content directory, to which SRC is copied.
      -R, -r, --recursive     Link the contents of directories recursively. If a
                              destination is specified then the directory tree
                              will be reproduced there. Otherwise, the individual
                              links will be placed in the default location for
                              their filetype. If this option is not specified and
                              SRC is a directory, then a link will be made to a
                              directory itself.
      -f, --force             Overwrite files without asking permission first.
      --help                  Show this message and exit.

### unload
    Usage: scribbler unload [OPTIONS]
    
      Unload the currently loaded notebook from Scribbler. Scribbler commands
      will no longer work on a notebook.
    
    Options:
      --help  Show this message and exit.

## Disclaimer
Scribbler is extremely new and still evolving. I make absolutely no guarantees
regarding its stability. If you find a bug, please do let me know through
GitHub's issue reporting mechanism.

Scribbler was written to meet my needs. I have placed it on GitHub in case
anyone else can get some use out of it. However, I am not intending to devote
much more time to Scribbler other than for addressing the To Do list below. As
such, I am unlikely to respond to feature requests. It doesn't hurt to suggest
them, but unless it is something which I would use myself, I'm not likely to
implement it. Pull requests implementing new features, on the other hand, are
welcome.

## To Do
- [ ] Creade a Markdown plugin which allows references to tables and code
	  blocks?
- [ ] Add option to force recreation of some or all PDF files
- [ ] Add a default to the `src`, `html`, and `pdf` commands that opens
      notes for today.
- [ ] Provide a way to rename and/or relocate an existing notebook
- [ ] Send the output of the `list` command to a pager
- [x] Write better documentation
- [ ] Reduce the font size
- [ ] Create a command to delete notes/appendices
- [ ] Create command to open `index.html` and `FullNotebook.pdf`
- [ ] Make MathJax scripts local so they can be used faster
- [ ] Change CSS so that `pre` content is line-wrapped when printed
- [ ] Initialize markdown-include so that paths evaluated relative to notebook base

