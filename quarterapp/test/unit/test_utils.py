#
#  Copyright (c) 2013 Markus Eliasson, http://www.quarterapp.com/
#
#  Permission is hereby granted, free of charge, to any person obtaining
#  a copy of this software and associated documentation files (the
#  "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so, subject to
#  the following conditions:
#
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
#  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import unittest

from quarterapp.utils import *

class TestUnit(unittest.TestCase):
    def test_hex(self):
        self.assertTrue(valid_color_hex("#fff"))
        self.assertTrue(valid_color_hex("#ffffff"))
        self.assertTrue(valid_color_hex("#000"))
        self.assertTrue(valid_color_hex("#123456"))
        
        self.assertFalse(valid_color_hex("fff"))
        self.assertFalse(valid_color_hex("cdcdcd"))
        self.assertFalse(valid_color_hex("#ggg"))
        self.assertFalse(valid_color_hex("#cccc"))
        self.assertFalse(valid_color_hex("0"))
        self.assertFalse(valid_color_hex(""))

    def test_hash_password(self):
        self.assertEqual( 88, len(hash_password("secret", "salt")) )
        self.assertEqual( 88, len(hash_password("anothersecret", "salt")) )
        self.assertEqual( hash_password("secret", "salt"), hash_password("secret", "salt"))
        self.assertNotEqual( hash_password("secret", "salt"), hash_password("secret", "pepper"))

    def test_valid_date(self):
        self.assertTrue(valid_date("2013-01-29"))
        self.assertTrue(valid_date("1999-12-29"))
        self.assertTrue(valid_date("2013-11-01"))
        self.assertTrue(valid_date("2012-02-29"))

        self.assertFalse(valid_date("2013-29-11"))
        self.assertFalse(valid_date("2013-9-1"))
        self.assertFalse(valid_date("2013-02-29"))
        self.assertFalse(valid_date("13-1-29"))
        self.assertFalse(valid_date("29/01/2013"))
        self.assertFalse(valid_date("01/29/2013"))
