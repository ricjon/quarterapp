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

ERROR_NO_ACTIVITY_TITLE     = ApiError(500, "Missing value for title")
ERROR_NO_ACTIVITY_COLOR     = ApiError(501, "Missing value for color")
ERROR_NOT_VALID_COLOR_HEX   = ApiError(502, "Invalid color hex format")
ERROR_NO_ACTIVITY_ID        = ApiError(503, "Missing activity id")
ERROR_DELETE_ACTIVITY       = ApiError(504, "Could not delete activity")

ERROR_NO_QUARTERS           = ApiError(600, "No quarters given")
ERROR_NOT_96_QUARTERS       = ApiError(601, "Expected 96 quarters")
ERROR_INVALID_SHEET_DATE    = ApiError(602, "Expected date in YYYY-MM-DD format")
