#!/usr/bin/python2

import sys
import re
import os

assert sys.version_info[:3] >= (2,2,0)

import BibTeX
import config

def getTemplate(name):
    f = open(name+".html")
    template = f.read()
    f.close()
    template_s, template_e = template.split("%(entries)s")
    return template_s, template_e

def writeBody(f, sections, section_urls):
    '''f: an open file 
       sections: list of (sectionname, [list of BibTeXEntry])
       section_urls: map from sectionname to external url'''
    for s, entries in sections:
        u = section_urls.get(s)
        sDisp = re.sub(r'\s+', ' ', s.strip())
        sDisp = sDisp.replace(" ", "&nbsp;")
        if u:
            print >>f, ('<li><h3><a name="%s"></a><a href="%s">%s</a></h3>'%(
                (BibTeX.url_untranslate(s), u, sDisp)))
        else:
            print >>f, ('<li><h3><a name="%s">%s</a></h3>'%(
                BibTeX.url_untranslate(s),sDisp))
        print >>f, "<ul class='expand'>"
        for e in entries:
            print >>f, e.to_html()
        print >>f, "</ul></li>"

def writeHTML(f, sections, sectionType, fieldName, choices, section_urls={}):
    """sections: list of (sectionname, [list of BibTeXEntry])'''
       sectionType: str
       fieldName: str
       choices: list of (choice, url)"""
    #
    secStr = []
    for s, _ in sections:
        hts = re.sub(r'\s+', ' ', s.strip())
        hts = s.replace(" ", "&nbsp;")
        secStr.append("<p class='l2'><a href='#%s'>%s</a></p>\n"%
                      ((BibTeX.url_untranslate(s),hts)))
    secStr = "".join(secStr)
    
    # 
    choiceStr = []
    for choice, url in choices:
        if url:
            choiceStr.append("<a href='%s'>%s</a>"%(url, choice))
        else:
            choiceStr.append(choice)
        
    choiceStr = ("&nbsp;|&nbsp;".join(choiceStr))

    fields = { 'command_line' :  "",
               'sectiontypes' :  sectionType,
               'choices' : choiceStr,
               'field': fieldName,
               'sections' : secStr,
         }

    header, footer = getTemplate("_template_")
    print >>f, header%fields
    writeBody(f, sections, section_urls)
    print >>f, footer%fields
    
bib = BibTeX.parseFile(config.MASTER_BIB)

##### Sorted views:

## By topic.

entries = BibTeX.sortEntriesBy(bib.entries, "www_section", "ZZZZZZZZZZZZZZZZZ")
entries = BibTeX.splitSortedEntriesBy(entries, "www_section")
if entries[-1][0].startswith("<span class='bad'>"):
    entries[-1] = ("Miscellaneous", entries[-1][1])

entries = [ (s, BibTeX.sortEntriesByAuthor(ents))
            for s, ents in entries
            ]

f = open(os.path.join(config.OUTPUT_DIR,"topic.html"), 'w')
writeHTML(f, entries, "Topics", "topic",
          (("By topic", None),
           ("By date", "./date.html"),
           ("By author", "./author.html")
           ))
f.close()

## By date.

entries = BibTeX.sortEntriesByDate(bib.entries)
entries = BibTeX.splitSortedEntriesBy(entries, 'year')
if entries[-1][0].startswith("<span class='bad'>"):
    entries[-1] = ("Unknown", entries[-1][1])
sections = [ ent[0] for ent in entries ]

first_year = int(entries[0][1][0]['year'])
try:
    last_year = int(entries[-1][1][0].get('year'))
except ValueError:
    last_year = int(entries[-2][1][0].get('year'))

years = map(str, range(first_year, last_year+1))
if entries[-1][0] == 'Unknown':
    years.append("Unknown")

f = open(os.path.join(config.OUTPUT_DIR,"date.html"), 'w')
writeHTML(f, entries, "Years", "date",
          (("By topic", "./topic.html"),
           ("By date", None),
           ("By author", "./author.html")
           ))
f.close()

## By author
entries, url_map = BibTeX.splitEntriesByAuthor(bib.entries)

f = open(os.path.join(config.OUTPUT_DIR,"author.html"), 'w')
writeHTML(f, entries, "Authors", "author",
          (("By topic", "./topic.html"),
           ("By date", "./date.html"),
           ("By author", None),
          ),
          url_map)
f.close()

## The big BibTeX file

entries = bib.entries[:]
entries = [ (ent.key, ent) for ent in entries ]
entries.sort()
entries = [ ent[1] for ent in entries ]
header,footer = getTemplate("_template_bibtex")
f = open(os.path.join(config.OUTPUT_DIR,"bibtex.html"), 'w')
print >>f, header % { 'command_line' : "" }
for ent in entries:
    print >>f, (
        ("<tr><td class='bibtex'><a name='%s'>%s</a>"
        "<pre class='bibtex'>%s</pre></td></tr>")
        %(BibTeX.url_untranslate(ent.key), ent.key, ent.format(90,8,1)))
print >>f, footer
f.close()

