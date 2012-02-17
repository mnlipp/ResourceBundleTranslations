"""
..
   This file is part of the Resource Bundle Translations package.
   Copyright (C) 2012 Michael N. Lipp

.. codeauthor:: mnl

Purpose of this module
======================

When I got started with python, I found the "standard" way of 
getting localized texts with :mod:`gettext` rather complicated.
Besides having a compilation step from po-files to mo-files, my
application would also have to install the mo-files eventually
in a system directory.

I looked for a good alternative for quite some time, but didn't
find one. So I decided to port the Java ResourceBundle approach
to Python, with some minor adaptations.

The translations are stored in files with the same format as
Java properties files. As an extension, utf-8 encoded properties
files are support (Java defines iso-8859-1 as standard encoding for
properties files. The encoding can be specified as for python
source files by adding a magic comment as first or second line
in the properties file. The comment must match the regular expression
``coding[:=]\s*([-\w.]+)`` to be recognized (e.g. "``coding: utf-8``".
 
"""
import codecs
import re

class Translations(object):

    _codingRegex = re.compile("coding[:=]\s*([-\w.]+)")

    def __init__(self, fp):
        self._translations = self._parse(fp)
        
    def _parse(self, fp):
        res = dict()
        key = u""
        value = u""
        escaped = False
        have_key = False
        skip_ws = True
        pending_ws = ""
        ignore_comment = False
        unicode_digits = 0
        unicode_buffer = ""
        encoding = "iso-8859-1"
        line_count = 0
        while True:
            line = fp.readline()
            if line == "": # EOF
                if key != "": # Save pending key/value
                    res[key] = value
                break;
            line_count += 1
            line = codecs.decode(line, encoding)
            skip_ws = True # Always skip white space at beginning of line
            for c in line: # Now look at the individual characters
                if unicode_digits > 0:
                    unicode_buffer += c
                    unicode_digits -= 1
                    if unicode_digits > 0:
                        continue
                    c = unichr(int(unicode_buffer, 16))
                    unicode_buffer = ""
                if c == '\r': # ignore CRs
                    continue
                if c == '\t' or c == '\f': # Map to white space
                    c = ' '
                if skip_ws:
                    if c == ' ':
                        continue
                    else:
                        skip_ws = False # Found first non white space character
                        if not ignore_comment: # i.e. is not continuation line
                            if c == '#' or c == '!': # Skip comment lines
                                if line_count <= 2:
                                    mo = self._codingRegex.search(line)
                                    if mo:
                                        encoding = mo.group(1) 
                                break
                    ignore_comment = False
                if escaped: # i.e., previous char was '\'
                    escaped = False
                    if c == '\n': # Next line is continuation even when ...
                        ignore_comment = True # ... looking like a comment
                        continue
                    if c == 'u':
                        unicode_digits = 4
                        continue
                else:
                    if c == " ": # whitespace is skipped around keys and values
                        pending_ws += " "
                        continue
                    if c == '\\':
                        escaped = True
                        continue
                    if (c == ':' or c == "=") and not have_key:
                        have_key = True
                        pending_ws = "" # skip white space after key
                        skip_ws = True # skip white space before value
                        continue
                    if c == '\n': # not escaped, end of key/value pair
                        if key != "":
                            res[key] = value
                            key = ""
                            value = ""
                            pending_ws = ""
                            have_key = False
                        break # continue with next line
                if not have_key:
                    key += (pending_ws + c)
                else:
                    value += (pending_ws + c)
                pending_ws = ""

        return res
