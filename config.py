
import re

MASTER_BIB = "./anonbib.bib"

OUTPUT_DIR = "."

AUTHOR_URLS = {
    'Berthold' : 'http://page.inf.fu-berlin.de/~berthold/',
    'Miguel.*Castro' : 'http://research.microsoft.com/users/mcastro/',
    'Chaum' : 'http://www.chaum.org',
    'Danezis' : 'http://www.cl.cam.ac.uk/~gd216/',
    'Dingledine' : 'http://www.freehaven.net/~arma/cv.html',
    'Desmedt' : 'http://www.cs.fsu.edu/~desmedt/',
    'Jakobsson' : 'http://www.cs.ucsd.edu/users/markus/',
    'K.*Kurosawa' : 'http://kuro.cis.ibaraki.ac.jp/~kurosawa/',
    'B.*Liskov' : 'http://www.pmg.lcs.mit.edu/barbara_liskov.html',
    'Mathewson' : 'http://www.wangafu.net/~nickm/',
    'Mazi&egrave;res' : 'http://www.scs.cs.nyu.edu/~dm/',
    'A.*Pfitzmann' : 'http://dud.inf.tu-dresden.de/~pfitza/',
    'B.*Pfitzmann' : 'http://www.zurich.ibm.com/~bpf/',
    'Rivest' : 'http://theory.lcs.mit.edu/~rivest/',
    'Serjantov' : 'http://www.cl.cam.ac.uk/users/aas23/',
    'Syverson' : 'http://www.syverson.org/',
    'David.*Wagner' : 'http://www.cs.berkeley.edu/~daw/',
    'Shoup' : 'http://www.shoup.net/',
    'B.*M&ouml;ller' : 'http://www.informatik.tu-darmstadt.de/TI/Mitarbeiter/moeller.html',
    'Michael.*Freedman' : 'http://www.scs.cs.nyu.edu/~mfreed/',
    
    }

INITIAL_STRINGS = {
     'jan' : 'January',         'feb' : 'February',
     'mar' : 'March',           'apr' : 'April',
     'may' : 'May',             'jun' : 'June',
     'jul' : 'July',            'aug' : 'August',
     'sep' : 'September',       'oct' : 'October',
     'nov' : 'November',        'dec' : 'December'
    }

OMIT_ENTRIES = ("proceedings", "journal")


### Don't edit below this line

AUTHOR_RE_LIST = [
    (re.compile(k, re.I), v,) for k, v in AUTHOR_URLS.iteritems()
    ]
