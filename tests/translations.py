# -*- coding: utf-8 -*-
"""
.. codeauthor: mnl
"""
import unittest
import os
from rbtranslations import Translations
import rbtranslations

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

    def testBundle(self):
        trans = rbtranslations.translation("test", __file__, ["de_AT", "fr_FR"])
        self.assertEqual(trans.gettext("pancake"), "Palatschinken")
        self.assertEqual(trans.ugettext("mobile phone"), "Handy")
        self.assertEqual(trans.ugettext("computer"), "ordinateur")
        self.assertEqual(trans.ugettext("unknown"), "unknown")
        self.assertEqual(trans.gettext("Result = "), "Ergebnis = ")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testParse']
    unittest.main()