PYTHON=python
VERSION=0.2cvs

all:
	$(PYTHON) writeHTML.py anonbib.cfg

clean:
	rm -f *~ */*~ *.pyc *.pyo

update:
	$(PYTHON) updateCache.py anonbib.cfg

test:
	$(PYTHON) test.py

veryclean: clean
	rm -f author.html date.html topic.html bibtex.html tmp.bib

TEMPLATES=_template_.html _template_bibtex.html
CSS=css/main.css css/pubs.css
BIBTEX=anonbib.bib
SOURCE=BibTeX.py config.py metaphone.py reconcile.py updateCache.py \
	writeHTML.py
EXTRAS=TODO README Makefile ChangeLog anonbib.cfg

DISTFILES=$(TEMPLATES) $(CSS) $(BIBTEX) $(SOURCE) $(EXTRAS)

dist: clean
	rm -rf anonbib-$(VERSION)
	mkdir anonbib-$(VERSION)
	tar cf - $(DISTFILES) | (cd anonbib-$(VERSION); tar xf -)
	mkdir anonbib-$(VERSION)/cache
	tar czf anonbib-$(VERSION).tar.gz anonbib-$(VERSION)
	rm -rf anonbib-$(VERSION)
