"""
..
   This file is part of the Resource Bundle Translations package.
   Copyright (C) 2012 Michael N. Lipp

.. codeauthor:: mnl

Purpose of this module
======================

When I got started with python, I found the "standard" way of 
getting localized texts with :mod:`gettext` rather complicated.
The directory layout and especially the extra compilation step 
from po-files to mo-files is very annoying and in my opinion 
not compensated by having smaller mapping files, at least not 
in applications with a limited number of texts. 

I looked for a good alternative for quite some time, but didn't
find one. So I decided to port the Java ResourceBundle approach
to Python, with some minor adaptations.

The translations are stored in files with the same format as
Java properties files. As an extension, utf-8 encoded properties
files are supported (Java defines iso-8859-1 as standard encoding for
properties files). The encoding can be specified as in python
source files by adding a magic comment as first or second line
in the properties file. The comment must match the regular expression
``coding[:=]\s*([-\w.]+)`` to be recognized (i.e. "``coding: utf-8``").
You may also use different encodings as long as they are supported
by the :mod:`codecs` module and use "\\\\n" as a line
separator.

Keys in properties files may contain spaces. This allows using the
default translation to be used as key as you usually do with gettext.
Escaped spaces ("\\\\ ") are treated like regular characters and can
be used to define keys or values that have leading or trailing spaces. 

Translations are obtained by calling :func:`rbtranslations.translation`.
The returned :class:`rbtranslations.Translations` provide a subset
of the methods provided by the built-in :class:`gettext.NullTranslations`.
"""
import codecs
import re
import os

__all__ = ["BaseTranslations", "Translations", "translation"]

class BaseTranslations(object):
    """
    This class defines a dummy translations class that simply
    maps any message to itself. It is also used as a base class
    for real Translations classes and thus defines the interface
    of the Translations classes from this module. 

    The class mimics the interface of the standard 
    :class:`gettext.NullTranslations` class as far as reasonable.
    Handling of encodings has drastically been reduced. With unicode
    strings being available, the only reasonable approach is
    to get the translated messages using this type. If other encodings
    are required for further processing, they should be applied when
    interfacing with the components that require these encodings. 
    """

    _fallback = None

    def add_fallback(self, fallback):
        """
        Append *fallback* to the chain of fallbacks for the current 
        translation object. A translation object consults 
        its fallback if it cannot provide a translation for a given message.
        (Identical to :class:`gettext.NullTranslations` from the standard
        library.)
        """
        if self._fallback:
            self._fallback.add_fallback(fallback)
        else:
            self._fallback = fallback

    def ugettext(self, message):
        """
        Return the translated message if defined in the instance's
        dictionary, else forward the call to the fallback (if set).
        :class:`BaseTranslations` simply returns the message.
        """
        if self._fallback:
            return self._fallback.ugettext(message)
        return unicode(message)
    
    def gettext(self, message):
        """ An alias for ugettext. """
        return self.ugettext(message)


class Translations(BaseTranslations):
    """
    The Translations class that takes its dictionary from a properties
    file object.
    """

    _codingRegex = re.compile("coding[:=]\s*([-\w.]+)")

    def __init__(self, fp, fallback=None):
        self._fallback = fallback
        self._translations = self._parse(fp)
        
    def _parse(self, fp):
        """
        Parse the file object *fp* as a properties file and insert
        the key value pairs found in this instance's dictionary.
        """
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

    def ugettext(self, message):
        """
        Return the translated message if defined in the properties
        file read by this instance, else forward the call to the 
        fallback (if set).
        """
        if self._translations.has_key(message):
            return self._translations[message]
        return super(Translations, self).ugettext(message)


def translation(basename, localedir, languages):
    """
    Return a chain of :class:`Translations` instances that are created 
    from the properties files with the given *basename* in the directory
    *localedir*. As a convenience, *localedir* may be the name of
    a directory or the name of a file in a directory. This allows
    ``__file__`` to be passed without any modification if the
    properties files reside in the same directory as the python
    module that requests translations.
    
    The third parameter *languages* is a list of strings that
    specifies acceptable languages for mappings.
    
    The chain of :class:`Translations` is found by searching, for
    each language, for properties files "*basename.lang_spec*.properties".
    The *lang_spec* part is initially the string from the the current
    element of *languages*. Then a trailing "_..." part is removed
    and the lookup is repeated until only the basic language identifier
    remains (e.g. "de_DE_var1", "de_DE", "de"). Finally, a file
    "*basename*.properties" is searched for. Any matching properties file
    is converted to a :class:`Translations` instance that is added as
    fallback to the first instance that has been found. Finally,
    an instance of :class:`BaseTranslations` is added as fallback
    and the :class:`Translations` instance at the beginning of the
    chain is returned.
    """
    trans = None
    localedir = os.path.abspath(localedir)
    if os.path.isfile(localedir):
        localedir = os.path.dirname(localedir)
    for lang in languages:
        lang.replace("-", "_")
        while True:
            props_file = os.path.join\
                (localedir, basename + "_" + lang + ".properties")
            try:
                with open(props_file) as fp:
                    if trans:
                        trans.add_fallback(Translations(fp))
                    else:
                        trans = Translations(fp)
            except IOError:
                pass
            lang_up = lang.rsplit("_", 1)[0]
            if lang_up == lang:
                break
            lang = lang_up
    if trans:
        trans.add_fallback(BaseTranslations())
    else:
        trans = BaseTranslations()
    return trans

