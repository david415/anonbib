#!/usr/bin/python2
# Copyright 2003-2004, Nick Mathewson.  See LICENSE for licensing info.

"""Download files in bibliography into a local cache.
"""

import os
import sys
import signal
import time

import BibTeX
import config
import urllib2
import getopt
import socket
import errno

os.umask(022)

FILE_TYPES = [ "txt", "html", "pdf", "ps", "ps.gz", "abstract" ]
BIN_FILE_TYPES = [ 'pdf', 'ps.gz' ]

class UIError(Exception):
    pass

def tryUnlink(fn):
    try:
        os.unlink(fn)
    except OSError:
        pass

def getCacheFname(key, ftype, section):
    return BibTeX.smartJoin(config.OUTPUT_DIR,config.CACHE_DIR,
                            section,
                            "%s.%s"%(key,ftype))

def downloadFile(key, ftype, section, url,
                 timeout=config.DOWNLOAD_CONNECT_TIMEOUT):
    fname = getCacheFname(key, ftype, section)
    fnameTmp = fname+".tmp"
    fnameURL = fname+".url"
    tryUnlink(fnameTmp)

    def sigalrmHandler(sig,_):
        pass
    signal.signal(signal.SIGALRM, sigalrmHandler)
    signal.alarm(timeout)
    try:
        try:
            infile = urllib2.urlopen(url)
        except IOError, e:
            raise UIError("Cannot connect to url %s: %s"%(url,e))
        except socket.error, e:
            if getattr(e,"errno",-1) == errno.EINTR:
                raise UIError("Connection timed out to url %s"%url)
            else:
                raise UIError("Error connecting to %s: %s"%(url, e))
    finally:
        signal.alarm(0)

    mode = 'w'
    if ftype in BIN_FILE_TYPES:
        mode = 'wb'
    outfile = open(fnameTmp, mode)
    try:
        while 1:
            s = infile.read(1<<16)
            if not s: break
            outfile.write(s)
    finally:
        infile.close()
        outfile.close()

    urlfile = open(fnameURL, 'w')
    print >>urlfile, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if "\n" in url: url = url.replace("\n", " ")
    print >>urlfile, url
    urlfile.close()

    os.rename(fnameTmp, fname)

def getURLs(entry):
    r = {}
    for ftype in FILE_TYPES:
        ftype2 = ftype.replace(".", "_")
        url = entry.get("www_%s_url"%ftype2)
        if url:
            r[ftype] = url.strip().replace("\n", " ")
    return r

def getCachedURL(key, ftype, section):
    fname = getCacheFname(key, ftype, section)
    urlFname = fname+".url"
    if not os.path.exists(fname) or not os.path.exists(urlFname):
        return None
    f = open(urlFname, 'r')
    lines = f.readlines()
    f.close()
    if len(lines) != 2:
        print >>sys.stderr, "ERROR: unexpected number of lines in", urlFname
    return lines[1].strip()

def downloadAll(bibtex, missingOnly=0):
    """returns list of tuples of key, ftype, url, error"""
    errors = []
    for e in bibtex.entries:
        urls = getURLs(e)
        key = e.key
        section = e.get("www_cache_section", ".")
        for ftype, url in urls.items():
            fname = getCacheFname(key, ftype, section)
            if missingOnly:
                cachedURL = getCachedURL(key, ftype, section)
                if cachedURL == url:
                    print >>sys.stderr,"Skipping",url
                    continue
                elif cachedURL is not None:
                    print >>sys.stderr,"URL for %s.%s has changed"%(key,ftype)
                else:
                    print >>sys.stderr,"No record for %s.%s"%(key,ftype)
            try:
                downloadFile(key, ftype, section, url)
                print "Downloaded",url
            except UIError, e:
                print >>sys.stderr, str(e)
                errors.append((key,ftype,url,str(e)))
            except (IOError, socket.error), e:
                msg = "Error downloading %s: %s"%(url,str(e))
                print >>sys.stderr, msg
                errors.append((key,ftype,url,msg))
    return errors

if len(sys.argv) == 2:
    print "Loading from %s"%sys.argv[1]
else:
    print >>sys.stderr, "Expected a single configuration file as an argument"
    sys.exit(1)
config.load(sys.argv[1])

bib = BibTeX.parseFile(config.MASTER_BIB)
downloadAll(bib,missingOnly=1)
