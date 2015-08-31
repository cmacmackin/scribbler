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

## ToDo:
- [ ] Write a Markdown plugin to provide figures and a referencing system
      for them.
- [ ] Write a Markdown or Pelican plugin to provide BibTeX referencing
- [ ] Write a pelican plugin which will create a PNG (or SVG?) preview from
      PS or PDF and use that as a link to the original file
- [ ] Design a Pelican template which produces good notebook-like output. This
      output should be suitable for conversion to a PDF and printing.
- [ ] Develop a wrapper to handle all of this smoothly
- [ ] Add a utility to this wrapper which copies files into the appropriate
      location in the notes

