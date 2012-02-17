# -*- coding: utf-8 -*-
"""
.. codeauthor: mnl
"""
import unittest
import os
from rbtranslations import Translations
import codecs

class Test(unittest.TestCase):


    def testNormal(self):
        inp_file = os.path.abspath \
            (os.path.join(os.path.dirname(__file__), "trans.properties"))
        with open(inp_file) as fp:
            res = Translations(fp)
        self.assertEqual(res._translations["very"], "# tricky")
        self.assertEqual(res._translations[" long key "], " long value ")
        self.assertEqual(res._translations["who"], "are you?")
        self.assertEqual(res._translations["Hello"], "there")
        self.assertEqual(res._translations[u"π"], "pi")
        self.assertEqual(res._translations["umlaute"], u"äöüÄÖÜ")

    def testUtf8(self):
        inp_file = os.path.abspath \
            (os.path.join(os.path.dirname(__file__), "trans-utf8.properties"))
        with open(inp_file) as fp:
            res = Translations(fp)
        self.assertEqual(res._translations[u"π"], "pi")
        self.assertEqual(res._translations["umlaute"], u"äöüÄÖÜ")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testParse']
    unittest.main()