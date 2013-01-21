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

class ApiError:
    """
    Represents a API error that is returned to the user.
    """
    def __init__(self, code, message):
        self.code = code
        self.message = message

SUCCESS_CODE = 0

ERROR_RETRIEVE_SETTING      = ApiError(101, "Could not retrieve setting")
ERROR_NO_SETTING_KEY        = ApiError(102, "No settings key given")
ERROR_NO_SETTING_VALUE      = ApiError(103, "No value specified for setting key")
ERROR_UPDATE_SETTING        = ApiError(104, "Could not update setting key")

ERROR_DISABLE_USER          = ApiError(300, "Could not disble the given user")
ERROR_DISABLE_NO_USER       = ApiError(301, "Could not disble user - no user given")
ERROR_ENABLE_USER           = ApiError(302, "Could not enable the given user")
ERROR_ENABLE_NO_USER        = ApiError(303, "Could not enable user - no user given")
ERROR_DELETE_USER           = ApiError(304, "Could not delete the given user")
ERROR_DELETE_NO_USER        = ApiError(305, "Could not delete user - no user given")

ERROR_NOT_AUTHENTICATED     = ApiError(400, "Not logged in")

ERROR_NO_ACTIVITY_NAME      = ApiError(500, "Missing value for name")
ERROR_NO_ACTIVITY_COLOR     = ApiError(501, "Missing value for color")
ERROR_NOT_VALID_COLOR_HEX   = ApiError(502, "Invalid color hex format")

