#!/usr/bin/env python
"""
   [PlantUML][] Extension for [Python-Markdown][]
   ==============================================

   This plugin implements a block extension which can be used to specify a [PlantUML][] diagram which will be
   converted into an image and inserted in the document.

   Syntax:

      ::uml:: [format="png|svg"] [classes="class1 class2 ..."] [alt="text for alt"]
          PlantUML script diagram
      ::end-uml::

   Example:

      ::uml:: format="png" classes="uml myDiagram" alt="My super diagram"
          Goofy ->  MickeyMouse: calls
          Goofy <-- MickeyMouse: responds
      ::end-uml::

   Options are optional, but if present must be specified in the order format, classes, alt.
   The option value may be enclosed in single or double quotes.

   Installation
   ------------
   You need to install [PlantUML][] (see the site for details) and [Graphviz][] 2.26.3 or later.
   The plugin expects a program `plantuml` in the classpath. If not installed by your package
   manager, you can create a shell script and place it somewhere in the classpath. For example,
   save te following into `/usr/local/bin/plantuml` (supposing [PlantUML][] installed into
   `/opt/plantuml`):

       #!/bin/bash
       java -jar /opt/plantuml/plantuml.jar ${@}

   For [Gentoo Linux][Gentoo] there is an ebuild at http://gpo.zugaina.org/dev-util/plantuml/RDep: you can download
   the ebuild and the `files` subfolder or you can add the `zugaina` repository with [layman][]
   (reccomended).

   [Python-Markdown]: http://pythonhosted.org/Markdown/
   [PlantUML]: http://plantuml.sourceforge.net/
   [Graphviz]: http://www.graphviz.org
   [Gentoo]: http://www.gentoo.org
   [layman]: http://wiki.gentoo.org/wiki/Layman
"""

import os
import re
import tempfile
from subprocess import Popen, PIPE
from zlib import adler32
import logging
import markdown
from markdown.util import etree, AtomicString



logger = logging.getLogger('MARKDOWN')


# For details see https://pythonhosted.org/Markdown/extensions/api.html#blockparser
class PlantUMLBlockProcessor(markdown.blockprocessors.BlockProcessor):
    # Regular expression inspired by the codehilite Markdown plugin
    RE = re.compile(r'''::uml::
                        \s*(classes=(?P<quot1>"|')(?P<classes>[\w\s]+)(?P=quot1))?
                        \s*(alt=(?P<quot2>"|')(?P<alt>[\w\s"']+)(?P=quot2))?
                    ''', re.VERBOSE)
    # Regular expression for identify end of UML script
    RE_END = re.compile(r'::end-uml::\s*$')

    def test(self, parent, block):
        return self.RE.search(block)

    def run(self, parent, blocks):
        block = blocks.pop(0)
        text = block

        # Parse configuration params
        m = self.RE.search(block)
        classes = m.group('classes') if m.group('classes') else self.config['classes']
        alt = m.group('alt') if m.group('alt') else self.config['alt']

        # Read blocks until end marker found
        while blocks and not self.RE_END.search(block):
            block = blocks.pop(0)
            text += '\n' + block
        else:
            if not blocks:
                raise RuntimeError("UML block not closed")

        # Remove block header and footer
        text = re.sub(self.RE, "", re.sub(self.RE_END, "", text))

        # Generate image from PlantUML script
        imagesrc = self.generate_uml_image(text).replace('xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"','')
        imagesrc = re.sub(r'textLength="\d+"','',imagesrc)
        # Create image tag and append to the document
        #etree.SubElement(parent, "svg", alt=alt, classes=classes)
        etree.register_namespace('','http://www.w3.org/2000/svg')
        etree.register_namespace('xlink','http://www.w3.org/1999/xlink')
        src = etree.fromstring(imagesrc)
        #print(etree.tostring(src))
        parent.append(src)


    def generate_uml_image(self, plantuml_code):
        plantuml_code = plantuml_code.encode('utf8')
        tf = tempfile.NamedTemporaryFile(delete=False)
        tf.write('@startuml\n'.encode('utf8'))
        tf.write(plantuml_code)
        tf.write('\n@enduml'.encode('utf8'))
        tf.flush()

        imgext = ".svg"
        outopt = "-tsvg"

        # make a name
        name = tf.name+imgext
        # build cmd line
        cmdline = ['plantuml', outopt, tf.name]

        try:
            p = Popen(cmdline, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
        except Exception as exc:
            raise Exception('Failed to run plantuml: %s' % exc)
        else:
            if p.returncode == 0:
                # diagram was correctly generated, we can remove the temporary file
                os.remove(tf.name)
                # renaming output image using an hash code, just to not pullate
                # output directory with a growing number of images
                with open(name,'r') as r:
                    src = r.read()
                os.remove(name)
                return src
            else:
                # the temporary file is still available as aid understanding errors
                raise RuntimeError('Error in "uml" directive: %s' % err)


# For details see https://pythonhosted.org/Markdown/extensions/api.html#extendmarkdown
class PlantUMLMarkdownExtension(markdown.Extension):
    # For details see https://pythonhosted.org/Markdown/extensions/api.html#configsettings
    def __init__(self, *args, **kwargs):
        self.config = {
            'classes': ["uml", "Space separated list of classes for the generated image. Defaults to 'uml'."],
            'alt': ["uml diagram", "Text to show when image is not available. Defaults to 'uml diagram'"],
        }

        super(PlantUMLMarkdownExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        blockprocessor = PlantUMLBlockProcessor(md.parser)
        blockprocessor.config = self.getConfigs()
        md.parser.blockprocessors.add('plantuml', blockprocessor, '>code')


def makeExtension(*args, **kwargs):
    return PlantUMLMarkdownExtension(*args, **kwargs)
