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
ending `$` (i.e. `$x^2$` will render, but $ x^2 $ will not). Math appearing on
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

## Command Line Interface

## To Do
- [ ] Creade a Markdown plugin which allows references to tables and code
	  blocks?
- [ ] Add option to force recreation of some or all PDF files
- [ ] Add a default to the `src`, `html`, and `pdf` commands that opens
      notes for today.
- [ ] Provide a way to rename and/or relocate an existing notebook
- [ ] Send the output of the `list` command to a pager
- [ ] Write better documentation
- [ ] Reduce the font size
- [ ] Create a command to delete notes/appendices
- [ ] Create command to open `index.html` and `FullNotebook.pdf`
- [ ] Make MathJax scripts local so they can be used faster
- [ ] Change CSS so that `pre` content is line-wrapped when printed
- [ ] Initialize markdown-include so that paths evaluated relative to notebook base

# scribbler
To date I have not been able to find a convenient piece of software with which
to take down notes about my scientific research. To this end, I have created
scribbler ("scribbler" being a Canadian term for a notebook or workbook). To
meet my requirements for scientific note-taking, it should do the following:

1. Allow notes to be written in Markdown
2. Be able to handle LaTeX equations
3. Be able to include PDF and/or PS figures
4. Provide a BibTeX reference system
5. Export to printable PDF files
6. Preferably be able to export to HTML as well
7. Handle code-snippets, with syntax highlighting
8. Be able to sort entries by date
9. Provide captions for images, with a referencing system
1. Be able to parse settings from a YAML file

The [Pelican](http://blog.getpelican.com/) static site generator already
provides numbers 1, 2 (with a plugin), 6, 7, and 8. Item 9 can be handled
by writing a plugin for Markdown. Item 3 can be handled by a Pelican plugin.
Item 4 could be handled by a plugin for either of these systems. Item 3 can
be achieved by using [pdfkit](https://github.com/JazzCore/python-pdfkit) to
convert Pelican's HTML output. I also plan to use my
[markdown-include](https://github.com/cmacmackin/markdown-include). A Pelican
template can be written such that the output will look appropriate for
scientific notes.

Scribbler will consist largely as a wrapper for running Pelican with the
necessary plugins and then creating PDFs from the HTML output. It will read
its settings from a YAML file. It will
also provide a command to quickly copy a file into your notes.

## Things I will use:
- [Pelican](https://github.com/getpelican/pelican)
- [MarkdownSuperscript](https://pypi.python.org/pypi/MarkdownSuperscript)/[MarkdownSubscript](https://pypi.python.org/pypi/MarkdownSuperscript)
- [mdx_del_ins](https://pypi.python.org/pypi/mdx_del_ins)
- [markdown-checklist](https://github.com/FND/markdown-checklist)
- [markdown.highlight](https://github.com/ribalba/markdown.highlight)
- [figureAltCaption](https://github.com/jdittrich/figureAltCaption), perhaps as
  a base from which to build my own plugin for creating and referencing figures?
- [render_math](https://github.com/getpelican/pelican-plugins/tree/master/render_math)
