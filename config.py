
import re

MASTER_BIB = "./anonbib.bib"

OUTPUT_DIR = "."

# relative to OUTPUT_DIR.
CACHE_DIR = "cache"

# Time to connect to a server while caching.
DOWNLOAD_CONNECT_TIMEOUT = 15

AUTHOR_URLS = {
    'Ross.*Anderson' : 'http://www.cl.cam.ac.uk/users/rja14/',
    'Alessandro.*Acquisti' : 'http://www.sims.berkeley.edu/~acquisti/',
    'Adam.*Back' : 'http://www.cypherspace.org/~adam/',
    'Berthold' : 'http://page.inf.fu-berlin.de/~berthold/',
    'Miguel.*Castro' : 'http://research.microsoft.com/users/mcastro/',
    'Chaum' : 'http://www.chaum.com/',
    'J.*Claessens' : 'http://www.esat.kuleuven.ac.be/~joclaess/',
    'R.*Clayton' : 'http://www.cl.cam.ac.uk/~rnc1/',
    'Danezis' : 'http://www.cl.cam.ac.uk/~gd216/',
    'Claudia.*Diaz' : 'http://www.esat.kuleuven.ac.be/~cdiaz/',
    'Dingledine' : 'http://www.freehaven.net/~arma/cv.html',
    'Desmedt' : 'http://www.cs.fsu.edu/~desmedt/',
    'Douceur' : 'http://research.microsoft.com/~johndo/',
    'Michael.*Freedman' : 'http://www.scs.cs.nyu.edu/~mfreed/',
    'Ian.*Goldberg' : 'http://www.cs.berkeley.edu/~iang/',
    'Christian.*Grothoff' : 'http://www.ovmj.org/~grothoff/',
    'D.*Hopwood' : 'http://www.users.zetnet.co.uk/hopwood/',
    'Jakobsson' : 'http://www.rsasecurity.com/rsalabs/staff/bios/mjakobsson/',
    'Juels' : 'http://www.rsasecurity.com/rsalabs/staff/bios/ajuels/',
    'K.*Kurosawa' : 'http://kuro.cis.ibaraki.ac.jp/~kurosawa/',
    'H.*Langos' : 'http://www.wh9.tu-dresden.de/~heinrich/',
    'B.*Liskov' : 'http://www.pmg.lcs.mit.edu/barbara_liskov.html',
    'Mathewson' : 'http://www.wangafu.net/~nickm/',
    'Mazi&egrave;res' : 'http://www.scs.cs.nyu.edu/~dm/',
    'B.*M&ouml;ller' : ('http://www.informatik.tu-darmstadt.de/TI/'
                        'Mitarbeiter/moeller.html'),
    'U.*M&ouml;ller' : 'http://www.ulfm.de/',
    'D.*Molnar' : 'http://hcs.harvard.edu/~dmolnar/papers.html',
    'R.*Morris' : 'http://www.pdos.lcs.mit.edu/~rtm/',
    'A.*Pfitzmann' : 'http://dud.inf.tu-dresden.de/~pfitza/',
    'B.*Pfitzmann' : 'http://www.zurich.ibm.com/~bpf/',
    'B.*Preneel' : 'http://www.esat.kuleuven.ac.be/~preneel/',
    'Daniel.*Simon' : 'http://research.microsoft.com/crypto/dansimon/me.htm',
    'Rackoff' : 'http://www.cs.toronto.edu/DCS/People/Faculty/rackoff.html',
    'Jean F' : 'http://www.geocities.com/j_f_raymond/',
    'M.*Rennhard' : 'http://www.tik.ee.ethz.ch/~rennhard/',
    'M.*Reiter' : 'http://www.ece.cmu.edu/~reiter/',
    'Rivest' : 'http://theory.lcs.mit.edu/~rivest/',
    'Avi.*Rubin' : 'http://avirubin.com/',
    'Serjantov' : 'http://www.cl.cam.ac.uk/users/aas23/',
    'S.*Seys' : 'http://www.esat.kuleuven.ac.be/~sseys/',
    'Shoup' : 'http://www.shoup.net/',
    'Syverson' : 'http://www.syverson.org/',
    'Tsudik' : 'http://www.ics.uci.edu/~gts/c.html',
    'M.*Waidner' : 'http://www.zurich.ibm.com/~wmi/',
    'David.*Wagner' : 'http://www.cs.berkeley.edu/~daw/',
    'M.*Waldman' : 'http://cs1.cs.nyu.edu/~waldman/',
    'M.*Wright' : 'http://www.cs.umass.edu/~mwright/',
    }

# List of paterns for author names _not_ to do an initial-tolerant
# match on when building section list.  E.g., if "J\\. Smith" is in
# this list, he won't be folded into "John Smith".
NO_COLLAPSE_AUTHORS = [

]

# Map from LaTeX-style name of author to collapse to canonical name.
COLLAPSE_AUTHORS = {
    "Nicholas Mathewson": "Nick Mathewson",
    }

# Map from author pattern to collation key.
ALPHEBETIZE_AUTHOR_AS = {
    "Zero.*Knowledge.*Systems": "Zero Knowledge Systems",
    }

INITIAL_STRINGS = {
    # MONTHS
     'jan' : 'January',         'feb' : 'February',
     'mar' : 'March',           'apr' : 'April',
     'may' : 'May',             'jun' : 'June',
     'jul' : 'July',            'aug' : 'August',
     'sep' : 'September',       'oct' : 'October',
     'nov' : 'November',        'dec' : 'December',

    # SECTIONS
     'sec_mix' : "Mix Networks: Design",
     'sec_mixattacks' : "Mix Networks: Attacks",
     'sec_stream' : "Stream-based anonymity",
     'sec_traffic' : "Traffic analysis",
     'sec_pub' : "Anonymous publication",
     'sec_nym' : "Pseudonymity"
}

OMIT_ENTRIES = ("proceedings", "journal")


### Don't edit below this line

AUTHOR_RE_LIST = [
    (re.compile(k, re.I), v,) for k, v in AUTHOR_URLS.items()
    ]

NO_COLLAPSE_AUTHORS_RE_LIST = [
    re.compile(pat, re.I) for pat in NO_COLLAPSE_AUTHORS
    ]

ALPHEBETIZE_AUTHOR_AS_RE_LIST = [
    (re.compile(k, re.I), v,) for k,v in ALPHEBETIZE_AUTHOR_AS.items()
    ]
