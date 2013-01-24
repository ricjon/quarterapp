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

import hashlib
import base64
import re

sha = hashlib.sha512()
color_hex_re = re.compile(r"^(#)([0-9a-fA-F]{3})([0-9a-fA-F]{3})?$")

def hash_password(password, salt):
    """
    Performs a password hash using the given salt.

    @param password The plain text password
    @param salt The applications salt
    @return The hashed password
    """
    sha.update(password + salt)
    hashed_password = base64.urlsafe_b64encode(sha.digest())
    return hashed_password

def valid_color_hex(color_code):
    """
    Validates that the given color code is a correct HEX code

    @return True if valid, else False
    """
    return color_hex_re.match(color_code)