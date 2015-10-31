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



## Installation

## Basic Use

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
