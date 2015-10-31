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
pip install .
```

Note that the [pdfkit](https://github.com/JazzCore/python-pdfkit) library
requires [wkhtmltopdf](http://wkhtmltopdf.org/) to be installed. Furthermore,
the default version of `wkhtmltopdf` on Debian and Ubuntu-based Linux
distributions has not been compiled with certain patches needed to provide
full functionality. Most of this functionality is not important for Scribbler,
except in two areas:

1. The inclusion of any links from the HTML in the PDF.
2. Without the patched version, the text in the output is very small and
   difficult to read.

For this reason, it is reccomended that you install a patched binary using
[this script](https://github.com/JazzCore/python-pdfkit/blob/master/travis/before-script.sh).

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
├── └── ...
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

## Writing Notes

## Command Line Interface

## To Do

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

## ToDo:
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
