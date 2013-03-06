#
#  Copyright (c) 2013 Markus Eliasson, http://www.quarterapp.com/
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    @return True if the date string is correctly formatted, else False
    """
    return extract_date(date) != None

def extract_date(date):
    """
    Extrac a date object based on the given date string, the string must be formatted
    YYYY-MM-DD else None will be returned.

    @param date The date in string format
    @return The date object with the given date, or None
    """
    try:
        parts = date.split("-")
        if len(parts) != 3:
            return None
        else:
            if len(parts[0]) == 4 and len(parts[1]) == 2 and len(parts[2]) == 2:
                date_obj = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                return date_obj
            else:
                return None
    except:
        return None

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
