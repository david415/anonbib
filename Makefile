
PYTHON=python2

all:
	$(PYTHON) writeHTML.py

clean:
	rm -f *~ */*~ *.pyc *.pyo

update: 
	$(PYTHON) updateCache.py

veryclean: clean
	rm -f author.html date.html topic.html bibtex.html tmp.bib
