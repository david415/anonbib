#!/usr/bin/python

import cStringIO
import re
import sys

import config

__all__ = ( 'ParseError', 'BibTeX', 'BibTeXEntry', 'htmlize',
            'ParsedAuthor', 'FileIter', 'Parser', 'parseFile',
            'splitBibTeXEntriesBy',
            'sortBibTexEntriesBy', )

MONTHS = [ None,
           "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]
            
class ParseError(Exception):
    pass

class BibTeX:
    def __init__(self):
        self.entries = []
        self.byKey = {}
    def addEntry(self, ent):
        k = ent.key
        if self.byKey.get(ent.key):
            print >> sys.stderr, "Already have an entry named %s"%k
            return
        self.entries.append(ent)
        self.byKey[ent.key] = ent
    def resolve(self):
        seen = {}
        for ent in self.entries:
            seen.clear()
            while ent.get('crossref'):
                try:
                    cr = self.byKey[ent['crossref'].lower()]
                except KeyError:
                    print "No such crossref: %s", ent['crossref']
                    break
                if seen.get(cr.key):
                    raise ParseError("Circular crossref at %s" % ent.key)
                seen[cr.key] = 1
                del ent.entries['crossref']
                ent.entries.update(cr.entries)
            ent.resolve()
        newEntries = []
        for ent in self.entries:
            if ent.type in config.OMIT_ENTRIES:
                del self.byKey[ent.key]
            else:
                newEntries.append(ent)
        self.entries = newEntries                

def splitEntriesBy(entries, field):
    result = {}
    for ent in entries:
        key = ent.get(field)
        try:
            result[key].append(ent)
        except:
            result[key] = [ent]
    return result

def splitSortedEntriesBy(entries, field):
    result = []
    curVal = "alskjdsakldj"
    curList = []
    for ent in entries:
        key = ent.get(field)
        if key == curVal:
            curList.append(ent)
        else:
            curVal = key
            curList = [ent]
            result.append((curVal, curList))
    return result

def sortEntriesBy(entries, field, default):
    tmp = []
    for ent in entries:
        tmp = [ (txtize(ent.get(field, default)), ent) for ent in entries ]
    tmp.sort()
    return [ t[1] for t in tmp ]

def sortEntriesByAuthor(entries):
    tmp = []
    for ent in entries:
        authors = [ txtize(" ".join(a.von+a.last+a.first+a.jr))
                    for a in ent.parsedAuthor ]
        tmp.append((tuple(authors), ent))
    tmp.sort()
    return [ t[1] for t in tmp ]

def sortEntriesByDate(entries):
    tmp = []
    for ent in entries:
        try:
            mon = MONTHS.index(ent.get("month"))
        except ValueError:
            print "Unknown month %r in %s"%(ent.get("month"), ent.key)
            mon = 0

        try:
            date = int(ent['year'])*13 + mon
        except KeyError:
            print "ERROR: No year field in %s"%ent.key
            date = 10000*13
        tmp.append((date, ent))
    tmp.sort()
    return [ t[1] for t in tmp ]
    

DISPLAYED_FIELDS = [ 'title', 'author', 'journal', 'booktitle',
'school', 'institution', 'organization', 'volume', 'number', 'year',
'month', 'address', 'chapter', 'edition', 'pages', 'editor',
'howpublished', 'key', 'publisher', 'type', 'note' ]

class BibTeXEntry:
    def __init__(self, type, key, entries):
        self.type = type
        self.key = key
        self.entries = entries
        self._get = self.entries.__getitem__
    def get(self, k, v=None):
        return self.entries.get(k,v)
    def __getitem__(self, k):
        return self._get(k)
    def __setitem__(self, k, v):
        self.entries[k] = v
    def __str__(self):
        return self.format(70,1)
    def format(self, width=70,v=0):
        d = ["@%s{%s,\n" % (self.type, self.key)]
        if v:
            df = DISPLAYED_FIELDS[:]
            for k in self.entries.keys():
                if k not in df:
                    df.append(k)
        else:
            df = DISPLAYED_FIELDS
        for f in df:
            if not self.entries.has_key(f):
                continue
            v = self.entries[f]
            d.append("  ")
            s = "%s = {%s}\n" % (f, v)
            d.append(_split(s,width))
        d.append("}\n")
        return "".join(d)
    def resolve(self):
        a = self.get('author')
        if a:
            self.parsedAuthor = parseAuthor(a)
            #print a
            #print "   => ",repr(self.parsedAuthor)
        else:
            self.parsedAuthor = None
    def check(self):
        ok = 1
        if self.type == 'inproceedings':
            fields = 'booktitle', 'year'
        elif self.type == 'article':
            fields = 'journal', 'year'
        elif self.type == 'techreport':
            fields = 'institution', 'number'
        elif self.type == 'misc':
            fields = 'howpublished',
        else:
            fields = ()
        fields += 'title', 'author'

        for field in fields:
            if not self.get(field):
                print "ERROR: %s has no %s field" % (self.key, field)
                self.entries[field] = "<span class='bad'>%s:??</span>"%field
                ok = 0

        return ok

    def biblio_to_html(self):
        if self.type == 'inproceedings':
            booktitle = self['booktitle']
            bookurl = self.get('bookurl')
            if bookurl:
                m = PROCEEDINGS_RE.match(booktitle)
                if m:
                    res = ["In the ", m.group(1),
                           '<a href="%s">'%bookurl, m.group(2), "</a>"]
                else:
                    res = ['In the <a href="%s">%s</a>' % (bookurl,booktitle)]
            else:
                res = ["In the ", booktitle ]

            if self.get("edition"):
                res.append(",")
                res.append(self['edition'])
            if self.get("address"):
                res.append(",")
                res.append(self['address'])
            res.append(", %s %s" % (self.get('month',""), self['year']))
            if not self.get('pages'):
                pass
            elif "-" in self['pages']:
                res.append(", pages&nbsp; %s"%self['pages'])
            else:
                res.append(", page&nbsp; %s"%self['pages'])
        elif self.type == 'article':
            res = ["In "]
            if self.get('journalurl'):
                res.append('<a href="%s">%s</a>'%
                           (self['journalurl'],self['journal']))
            else:
                res.append(self['journal'])
            if self.get('volume'):
                res.append(" <b>%s</b>"%self['volume'])
            if self.get('number'):
                res.append("(%s)"%self['number'])
            res.append(", %s %s" % (self.get('month',""), self['year']))
            if not self.get('pages'):
                pass
            elif "-" in self['pages']:
                res.append(", pages&nbsp; %s"%self['pages'])
            else:
                res.append(", page&nbsp; %s"%self['pages'])
        elif self.type == 'techreport':
            res = [ "%s %s %s" % (self['institution'],
                                  self.get('type', 'technical report'),
                                  self['number']) ]
            if self.get('month') or self.get('year'):
                res.append(", %s %s" % (self.get('month', ''),
                                        self.get('year', '')))
        elif self.type == 'mastersthesis' or self.type == 'phdthesis':
            if self.get('type'):
                res = [self['type']]
            elif type == 'mastersthesis':
                res = ["Masters's thesis"]
            else:
                res = ["Ph.D. thesis"]
            if self.get('school'):
                res.append(", %s"%(self['school']))
            if self.get('month') or self.get('year'):
                res.append(", %s %s" % (self.get('month', ''),
                                        self.get('year', '')))
        elif self.type == 'misc':
            res = [self['howpublished']]
            if self.get('month') or self.get('year'):
                res.append(", %s %s" % (self.get('month', ''),
                                        self.get('year', '')))
            if not self.get('pages'):
                pass
            elif "-" in self['pages']:
                res.append(", pages&nbsp; %s"%self['pages'])
            else:
                res.append(", page&nbsp; %s"%self['pages'])
        else:
            res = ["&lt;Odd type %s&gt;"%self.type]

        res[0:0] = ["<span class='biblio'>"]
        res.append("</span>")
        
        res.append(" <span class='availability'>"
                   "(<a href='__'>BibTeX&nbsp;entry</a>)"
                   "</span>")
        return htmlize("".join(res))

    def to_html(self):
        res = ["<li><p class='entry'><span class='title'>%s</span>"%(
            htmlize(self['title']))]
        availability = []
        for key, name in (('www_abstract_url', 'abstract'),
                          ('www_html_url', 'HTML'),
                          ('www_pdf_url', 'PDF'),
                          ('www_ps_url', 'PS'),
                          ('www_txt_url', 'TXT'),
                          ('www_ps_gz_url', 'gzipped&nbsp;PS')):
            url = self.get(key)
            if not url: continue
            availability.append('<a href="%s">%s</a>' %(url,name))
        if availability:
            res.append(" <span class='availability'>(")
            res.append(",&nbsp;".join(availability))
            res.append(")</span>")
        res.append("<br><span class='author'>by ")

        #res.append("\n<!-- %r -->\n" % self.parsedAuthor)
        htmlAuthors = []
        for author in self.parsedAuthor:
            f,v,l,j = author.first,author.von,author.last,author.jr
            a = " ".join(f+v+l)
            if j:
                a = "%s, %s" %(a,j)
            a = htmlize(a)
            htmlAuthor = None
            for pat, url in config.AUTHOR_RE_LIST:
                if pat.search(a):
                    htmlAuthor = '<a href="%s">%s</a>' % (url, a)
                    break
            if not htmlAuthor:
                htmlAuthor = a
            htmlAuthors.append(htmlAuthor)
        if len(htmlAuthors) == 1:
            res.append(htmlAuthors[0])
        elif len(htmlAuthors) == 2:
            res.append(" and ".join(htmlAuthors))
        else:
            res.append(", ".join(htmlAuthors[:-1]))
            res.append(", and ")
            res.append(htmlAuthors[-1])

        if res[-1][-1] != '.':
            res.append(".")
        res.append("</span><br>\n")
        res.append(self.biblio_to_html())
        res.append("</p></li>\n\n")
        return "".join(res)

RE_LONE_AMP = re.compile(r'&([^a-z0-9])')
RE_LONE_I = re.compile(r'\\i([^a-z0-9])')
RE_ACCENT = re.compile(r'\\([\'`~^"])(.)')
ACCENT_MAP = { "'": 'acute', "`" : 'grave', "~": 'tilde',
               "^": 'circ',  '"' : 'uml' }
RE_TEX_CMD = re.compile(r"(?:\\[a-zA-Z@]+|\\.)")
RE_PAGE_SPAN = re.compile(r"(\d)--(\d)")
def htmlize(s):
    s = RE_LONE_AMP.sub(lambda m: "&amp;%s" % m.group(1), s)
    s = RE_LONE_I.sub(lambda m: "i%s" % m.group(1), s)
    s = RE_ACCENT.sub(lambda m: "&%s%s;" %(m.group(2),
                                           ACCENT_MAP[(m.group(1))]),
                       s)
    s = RE_TEX_CMD.sub("", s)
    s = s.translate(ALLCHARS, "{}")
    s = RE_PAGE_SPAN.sub(lambda m: "%s-%s"%(m.groups()), s)
    return s

def txtize(s):
    s = RE_LONE_I.sub(lambda m: "%s" % m.group(1), s)
    s = RE_ACCENT.sub(lambda m: "%s" % m.group(2), s)
    s = RE_TEX_CMD.sub("", s)
    s = s.translate(ALLCHARS, "{}")
    return s
    

PROCEEDINGS_RE = re.compile(
                        r'((?:proceedings|workshop record) of(?: the)? )(.*)',
                        re.I)
                     

class ParsedAuthor:
    def __init__(self, first, von, last, jr):
        self.first = first
        self.von = von
        self.last = last
        self.jr = jr
    def __repr__(self):
        return "ParsedAuthor(%r,%r,%r,%r)"%(self.first,self.von,
                                            self.last,self.jr)
    def __str__(self):
        return " ".join(self.first+self.von+self.last+self.jr)

def _split(s,w=79):
    r = []
    s = s.replace("\n", " ")
    while len(s) > w:
        for i in xrange(w-1, 0, -1):
            if s[i] == ' ':
                r.append(s[:i])
                s = s[i+1:]
                break
        else:
            r.append(s[:w])
            s = s[w:]
    r.append(s)
    r.append("")
    return "\n".join(r)
            
class FileIter:
    def __init__(self, fname=None, file=None, it=None, string=None):
        if fname:
            file = open(fname, 'r')
        if string:
            file = cStringIO.StringIO(string)
        if file:
            it = iter(file.xreadlines())
        self.iter = it
        assert self.iter
        self.lineno = 0
        self._next = it.next
    def next(self):
        self.lineno += 1
        return self._next()
    

def parseAuthor(s):
    items = []

    #print "A", `s`
    s = s.strip()
    while s:
        s = s.strip()
        bracelevel = 0
        for i in xrange(len(s)):
            if s[i] == '{':
                bracelevel += 1
            elif s[i] == '}':
                bracelevel -= 1
            elif bracelevel <= 0 and s[i] in " \t\n,":
                break
        if i+1 == len(s):
            items.append(s)
        else:
            items.append(s[0:i])            
        if (s[i] == ','):
            items.append(',')
        s = s[i+1:]

    #print "B", items

    authors = [[]]
    for item in items:
        if item == 'and':
            authors.append([])
        else:
            authors[-1].append(item)

    #print "C", authors

    parsedAuthors = []
    # Split into first, von, last, jr
    for author in authors:
        #print author
                
        commas = 0
        fvl = []
        vl = []
        f = []
        v = []
        l = []
        j = []
        cur = fvl
        for item in author:
            if item == ',':
                if commas == 0:
                    vl = fvl
                    fvl = []
                    cur = f
                else:
                    j.extend(f)
                    f = []
            else:
                cur.append(item)
        if commas == 0:
            split_von(f,v,l,fvl)
        else:
            split_von(None,v,l,vl)

        parsedAuthors.append(ParsedAuthor(f,v,l,j))
        #print "   ====> ", parsedAuthors[-1]

    return parsedAuthors

ALLCHARS = "".join(map(chr,range(256)))
LC_CHARS = "abcdefghijklmnopqrstuvwxyz"
SV_DELCHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
               "abcdefghijklmnopqrstuvwxyz"
               "@")
RE_ESCAPED = re.compile(r'\\.')
def split_von(f,v,l,x):
    in_von = 0
    while x:
        tt = t = x[0]
        del x[0]
        if tt[:2] == '{\\':
            tt = tt.translate(ALLCHARS, SV_DELCHARS)
            tt = RE_ESCAPED.sub("", tt)
            tt = tt.translate(ALLCHARS, "{}")
        if tt.translate(ALLCHARS, LC_CHARS) == "":
            v.append(t)
            in_von = 1
        elif in_von and f is not None:
            l.append(t)
            l.extend(x)
            return
        else:
            f.append(t)
    if not in_von:
        l.append(f[-1])
        del f[-1]

class Parser:
    def __init__(self, fileiter, initial_strings):
        self.strings = config.INITIAL_STRINGS.copy()
        self.strings.update(initial_strings)
        self.fileiter = fileiter
        self.entries = {}
        self.result = BibTeX()
        self.litStringLine = 0
        self.entryLine = 0

    def _parseKey(self, line):
        it = self.fileiter
        line = _advance(it,line)
        m = KEY_RE.match(line)
        if not m:
            raise ParseError("Expected key at line %s"%self.fileiter.lineno)
        key, line = m.groups()
        return key, line

    def _parseValue(self, line):
        it = self.fileiter
        bracelevel = 0
        data = []
        while 1:
            line = _advance(it,line)
            line = line.strip()
            assert line

            # Literal string?
            if line[0] == '"':
                line=line[1:]
                self.litStringLine = it.lineno
                while 1:
                    if bracelevel:
                        m = BRACE_CLOSE_RE.match(line)
                        if m:
                            data.append(m.group(1))
                            data.append('}')
                            line = m.group(2)
                            bracelevel -= 1 
                            continue
                    else:
                        m = STRING_CLOSE_RE.match(line)
                        if m:
                            data.append(m.group(1))
                            line = m.group(2)
                            break
                    m = BRACE_OPEN_RE.match(line)
                    if m:
                        data.append(m.group(1))
                        line = m.group(2)
                        bracelevel += 1
                        continue
                    data.append(line)
                    line = it.next()
                self.litStringLine = 0
            elif line[0] == '{':
                bracelevel += 1
                line = line[1:]
                while bracelevel:
                    m = BRACE_CLOSE_RE.match(line)
                    if m:
                        #print bracelevel, "A", repr(m.group(1))
                        data.append(m.group(1))
                        bracelevel -= 1
                        if bracelevel > 0:
                            #print bracelevel, "- '}'"
                            data.append('}')
                        line = m.group(2)
                        continue
                    m = BRACE_OPEN_RE.match(line)
                    if m:
                        bracelevel += 1
                        #print bracelevel, "B", repr(m.group(1))
                        data.append(m.group(1))
                        line = m.group(2)
                        continue
                    else:
                        #print bracelevel, "C", repr(line)
                        data.append(line)
                        line = it.next()
            elif line[0] == '#':
                print >>sys.stderr, "Weird concat on line %s"%it.lineno
            elif line[0] in "},":
                if not data:
                    print >>sys.stderr, "No data after field on line %s"%(
                        it.lineno)
            else:
                m = RAW_DATA_RE.match(line)
                if m:
                    s = self.strings.get(m.group(1).lower())
                    if s is not None:
                        data.append(s)
                    else:
                        data.append(m.group(1))
                    line = m.group(2)
                else:
                    raise ParseError("Questionable line at line %s"%it.lineno)
                

            # Got a string, check for concatenation.
            line = _advance(it,line)
            line = line.strip()
            assert line
            if line[0] == '#':
                line = line[1:]
            else:
                return "".join(data), line

    def _parseEntry(self, line): #name, strings, entries
        it = self.fileiter
        self.entryLine = it.lineno
        line = _advance(it,line)
        m = BRACE_BEGIN_RE.match(line)
        if not m:
            raise ParseError("Expected an opening brace at line %s"%it.lineno)
        line = m.group(1)

        proto = { 'string' : 'p',
                  'preamble' : 'v',
                  }.get(self.curEntType, 'kp*')

        v = []
        while 1:
            line = _advance(it,line)

            m = BRACE_END_RE.match(line)
            if m:
                line = m.group(1)
                break
            if not proto:
                raise ParseError("Overlong entry starting on line %s"
                                 % self.entryLine)
            elif proto[0] == 'k':
                key, line = self._parseKey(line)
                v.append(key)
            elif proto[0] == 'v':
                value, line = self._parseValue(line)
                v.append(value)
            elif proto[0] == 'p':
                key, line = self._parseKey(line)
                v.append(key)
                line = _advance(it,line)
                line = line.lstrip()
                if line[0] == '=':
                    line = line[1:]
                value, line = self._parseValue(line)
                v.append(value)
            else:
                assert 0
            line = line.strip()
            if line and line[0] == ',':
                line = line[1:]
            if proto and proto[1:] != '*':
                proto = proto[1:]
        if proto and proto[1:] != '*':
            raise ParseError("Missing arguments to %s on line %s" % (
                             self.curEntType, self.entryLine))

        if self.curEntType == 'string':
            self.strings[v[0]] = v[1]
        elif self.curEntType == 'preamble':
            pass
        else:
            key = v[0]
            d = {}
            for i in xrange(1,len(v),2):
                d[v[i].lower()] = v[i+1]
            ent = BibTeXEntry(self.curEntType, key, d)
            self.result.addEntry(ent)

        return line
                
    def parse(self):
        try:
            self._parse()
        except StopIteration:
            if self.litStringLine:
                raise ParseError("Unexpected EOF in string (%s)" %
                                 self.litStringLine)
            elif self.entryLine:
                raise ParseError("Unexpected EOF at line %s (%s)" % (
                                 self.fileiter.lineno, self.entryLine))

        return self.result

    def _parse(self):
        it = self.fileiter
        line = it.next()
        while 1:
            while not line or line.isspace() or OUTER_COMMENT_RE.match(line):
                line = it.next()
            m = ENTRY_BEGIN_RE.match(line)
            if m:
                self.curEntType = m.group(1).lower()
                line = m.group(2)
                line = self._parseEntry(line)
                self.entryLine = 0
            else:
                raise ParseError("Bad input at line %s (expected a new entry.)"
                                 % it.lineno)
            
def _advance(it,line):
    while not line or line.isspace() or COMMENT_RE.match(line):
        line = it.next()
    return line

OUTER_COMMENT_RE = re.compile(r'^\s*[\#\%]')
COMMENT_RE = re.compile(r'^\s*\%')
ENTRY_BEGIN_RE = re.compile(r'''^\s*\@([^\s\"\%\'\(\)\,\=\{\}]+)(.*)''')
BRACE_BEGIN_RE = re.compile(r'\s*\{(.*)')
BRACE_END_RE = re.compile(r'\s*\}(.*)')
KEY_RE = re.compile(r'''\s*([^\"\#\%\'\(\)\,\=\{\}\s]+)(.*)''')

STRING_CLOSE_RE = re.compile(r'^([^\{\}\"]*)\"(.*)')
BRACE_CLOSE_RE = re.compile(r'^([^\{\}]*)\}(.*)')
BRACE_OPEN_RE = re.compile(r'^([^\{\}]*\{)(.*)')
RAW_DATA_RE = re.compile(r'^([^\s\},]+)(.*)')

def parseFile(filename):
    f = FileIter(fname=filename)
    p = Parser(f, {})
    r = p.parse()
    r.resolve()
    for e in r.entries:
        e.check()
    return r    

if __name__ == '__main__':
    import sys
    if len(sys.argv)>1:
        fname=sys.argv[1]
    else:
        fname="testbib/pdos.bib"

    r = parseFile(fname)
        
    for e in r.entries:
        if e.type in ("proceedings", "journal"): continue
        print e.to_html()

