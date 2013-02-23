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

import datetime
import hashlib
import base64
import re
import math
import os

color_hex_match_re = re.compile(r"^(#)([0-9a-fA-F]{3})([0-9a-fA-F]{3})?$")

def hash_password(password, salt):
    """
    Performs a password hash using the given salt.

    @param password The plain text password
    @param salt The applications salt
    @return The hashed password
    """
    sha = hashlib.sha512()
    sha.update(password + salt)
    hashed_password = base64.urlsafe_b64encode(sha.digest())
    return hashed_password

def valid_color_hex(color_code):
    """
    Validates that the given color code is a correct HEX code. For this
    function the hex code must start with a hash (#)

    @return True if valid, else False
    """
    return color_hex_match_re.match(color_code)

def valid_date(date):
    """
    Check if the given string is a valid date format YYYY-MM-DD

    @param date The date in string format
    @return True if the date string is correctly formatted
    """
    try:
        parts = date.split("-")
        if len(parts) != 3:
            raise ValueErrror("Date should be in YYYY-MM-DD")
        else:
            if len(parts[0]) == 4 and len(parts[1]) == 2 and len(parts[2]) == 2:
                date_obj = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                return True
            else:
                raise ValueErrror("Date should be in YYYY-MM-DD")
    except:
        return False

def get_dict_from_sequence(seq, key):
    # from http://stackoverflow.com/a/4391722
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))


def luminance_color(color_code, lum):
    """
    Change the luminance for the given color in HEX. Use positive for lighter and
    negative to generate a darker color.

    @param color_code The color code in HEX
    @param lum Percentage luminance to alter. 
    @return The color code in HEX for the new color
    """
    color_code = color_code.replace("#", "")
    lum = lum or 0;
    
    if len(color_code) == 3:
        color_code = color_code[0]+color_code[0]+color_code[1]+color_code[1]+color_code[2]+color_code[2]

    color = "#"
    for i in range(3):
        c = int(color_code[i * 2 : (i * 2) + 2], 16)
        c = int(round( min( max(0, c + (c * lum)), 255)))
        c = hex(c)[2:]
        color += str("00" + c)[len(c):]

    return color

def activation_code():
    """
    Generate and return a URL friendly activation code

    @return The activation code
    """
    code = os.urandom(16).encode("base64")
    code = re.sub("[\W\d]", "", code.strip())
    return code
