#!/usr/bin/python

import BibTeX
import config

bib = BibTeX.parseFile("anonbib.bib")

f = open("_template_.html")
template = f.read()
f.close()

f = open("z.html", 'w')

template_s, template_e = template.split("%(entries)s")

print >>f, template_s

entries = BibTeX.splitEntriesBy(bib.entries, "www_section")
sections = entries.keys()
sections.sort()
if entries.has_key(None):
    for ent in entries[None]:
        ent['www_section'] = "Miscellaneous"

    entries["Miscellaneous"] = entries[None]
    del entries[None]
    sections.append("Miscellaneous")
    sections = filter(None, sections)

for s in sections:
    #XXX print '<h3><a name="', url_untranslate($section), '">';
    print >>f, '<h3>%s</h3>'%s
    print >>f, "<ul class='expand'>"
    for e in entries[s]:
        print >>f, e.to_html()
    print >>f, "</ul>"
                     

print >>f, template_e

