#!/usr/bin/python

import re

import BibTeX
import config

TEMPLATE_S, TEMPLATE_E = None, None

def getTemplate():
    global TEMPLATE_S
    global TEMPLATE_E
    if not TEMPLATE_S:
        f = open("_template_.html")
        template = f.read()
        f.close()
        TEMPLATE_S, TEMPLATE_E = template.split("%(entries)s")
    return TEMPLATE_S, TEMPLATE_E

def url_untranslate(s):
    s = s.replace(" ", "+")
    s = re.sub(r'([%<>])',
               lambda m: "%%%02x"%ord(m.group(1)),
               s)
    return s

def writeBody(f, sections):
    '''f: an open file 
       sections: list of (sectionname, [list of BibTeXEntry])'''
    for s, entries in sections:
        print >>f, ('<h2><a name="%s">%s</a></h2>'%(url_untranslate(s),s))
        print >>f, "<ul class='expand'>"
        for e in entries:
            print >>f, e.to_html()
        print >>f, "</ul>"

def writeHTML(f, sections, sectionType, fieldName, choices):
    """sections: list of (sectionname, [list of BibTeXEntry])'''
       sectionType: str
       fieldName: str
       choices: list of (choice, url)"""
    #
    secStr = []
    for s, _ in sections:
        secStr.append("<p class='l2'><a href='#%s'>%s</a></p>\n"%
                      ((url_untranslate(s),s)))
    secStr = "".join(secStr)
    
    # 
    choiceStr = []
    for choice, url in choices:
        if url:
            choiceStr.append("<a href='%s'>%s</a>"%(url, choice))
        else:
            choiceStr.append(choice)
        
    choiceStr = "<p align='center'>%s</p>" % (" | ".join(choiceStr))

    fields = { 'command_line' :  "",
               'sectiontypes' :  sectionType,
               'choices' : choiceStr,
               'field': fieldName,
               'sections' : secStr,
         }

    header, footer = getTemplate()
    print >>f, header%fields
    writeBody(f, sections)
    print >>f, footer%fields
    
bib = BibTeX.parseFile(config.MASTER_BIB)

##### Sorted views:

## By topic.

entries = BibTeX.sortEntriesBy(bib.entries, "www_section", "ZZZZZZZZZZZZZZZZZ")
entries = BibTeX.splitSortedEntriesBy(entries, "www_section")
if entries[-1][0] is None:
    entries[-1] = ("Miscellaneous", entries[-1][1])

entries = [ (s, BibTeX.sortEntriesByAuthor(ents))
            for s, ents in entries
            ]

f = open("topic.html", 'w')
writeHTML(f, entries, "Topics", "topic",
          (("By topic", None),
           ("By date", "./date.html")))
f.close()

## By date.

entries = BibTeX.sortEntriesByDate(bib.entries)
entries = BibTeX.splitSortedEntriesBy(entries, 'year')
if entries[-1][0] == None:
    entries[-1] = ("Unknown", entries[-1][1])
sections = [ ent[0] for ent in entries ]

first_year = int(entries[0][1][0]['year'])
last_year = int(entries[-1][1][0].get('year',
                                      entries[-2][1][0]['year']))
years = map(str, range(first_year, last_year+1))
if entries[-1][0] == 'Unknown':
    years.append("Unknown")

f = open("date.html", 'w')
writeHTML(f, entries, "Years", "date",
          (("By topic", "./topic.html"),
           ("By date", None)))
f.close()

## The big BibTeX
