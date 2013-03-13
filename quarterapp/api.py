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

import logging
import sys
import os
import json
import string
from collections import Counter

import tornado.web
import tornado.escape
from tornado.options import options
from tornado.web import HTTPError

from basehandlers import *
from storage import *
from quarter_errors import *
from quarter_utils import *

class ActivityApiHandler(AuthenticatedHandler):
    """
    The activity API handler implements all supported operations on activities.
    """
    @authenticated_user
    def get(self):
        """
        Get the complete list of activities
        """
        user_id  = self.get_current_user_id()
        activities = get_activities(self.application.db, user_id)
        if not activities:
            activities = []
        self.write( { "activities" : activities } )
        self.finish()

    @authenticated_user
    def post(self):
        """
        Create a new activity
        """
        user_id  = self.get_current_user_id()
        title = self.get_argument("title", "")
        color = self.get_argument("color", "")

        errors = []

        if not title or len(title) == 0:
            errors.append( ERROR_NO_ACTIVITY_TITLE )
        if not color or len(color) == 0:
            errors.append( ERROR_NO_ACTIVITY_COLOR )
        if not valid_color_hex(color):
            errors.append( ERROR_NOT_VALID_COLOR_HEX )
        
        if len(errors) > 0:
            self.respond_with_errors(errors)
        else:
            activity_id = add_activity(self.application.db, user_id, title, color)
            activity = get_activity(self.application.db, user_id, activity_id)
            self.write( { "activity" : activity } )
            self.finish()

    @authenticated_user
    def put(self, activity_id):
        """
        Update a given activity
        """
        user_id  = self.get_current_user_id()
        title = self.get_argument("title", "")
        color = self.get_argument("color", "")
        disabled = self.get_argument("disabled", "")
        errors = []

        if not title or len(title) == 0:
            errors.append( ERROR_NO_ACTIVITY_TITLE )
        if not color or len(color) == 0:
            errors.append( ERROR_NO_ACTIVITY_COLOR )
        if not disabled or len(disabled) == 0:
            errors.append( ERROR_NO_ACTIVITY_DISABLED )
        if not valid_color_hex(color):
            errors.append( ERROR_NOT_VALID_COLOR_HEX )
        
        if len(errors) > 0:
            self.respond_with_errors(errors)
        else:
            update_activity(self.application.db, user_id, activity_id, title, color, disabled)
            activity = get_activity(self.application.db, user_id, activity_id)
            self.write( { "activity" : activity } )
            self.finish()

    @authenticated_user
    def delete(self, activity_id):
        """
        Delete a given activity
        """
        user_id  = self.get_current_user_id()
        errors = []

        if not activity_id or len(activity_id) == 0:
            errors.append( ERROR_NO_ACTIVITY_ID )

        try:
            if len(errors) > 0:
                self.respond_with_errors(errors)
            else:
                delete_activity(self.application.db, user_id, activity_id)
                self.write_success()
        except:
            logging.warn("Could not delete activity: %s", sys.exc_info())
            self.respond_with_error(ERROR_DELETE_ACTIVITY)

class BaseSheetHandler(AuthenticatedHandler):
    def _default_sheet(self):
        quarters = []
        for i in range(0, 96):
            quarters.append({ "id" : -1, "color" : "#fff", "border-color" : "#ccc"})
        return quarters

    def _sheet_summary(self, quarters, activity_dict):
        summary_list = []
        summary_dict = Counter(quarters)
        summary_total = 0
        for activity_id in summary_dict:
            if activity_id == "-1":
                continue

            activity_color = "#ccc"
            activity_title = "Unknown"

            if long(activity_id) in activity_dict:
                activity_color = activity_dict[long(activity_id)]["color"]
                activity_title = activity_dict[long(activity_id)]["title"]

            activity_summary = float(summary_dict[activity_id] / 4.0)
            summary_total += activity_summary
            summary_list.append({ "id" : activity_id, "color" : activity_color,
                "title" : activity_title, "sum" : "%.2f" % activity_summary})
        return summary_list, "%.2f" % summary_total

class SheetApiHandler(BaseSheetHandler):

    @authenticated_user
    def put(self, date):
        """
        Update a sheet with the quarters passed and return a map containing
        the unique occurance of each activity.

        @param date The sheet date in format YYYY-MM-DD
        @return a JSON map containing the unique count for each activity
        """
        user_id  = self.get_current_user_id()

        if not valid_date(date):
            self.respond_with_error(ERROR_INVALID_SHEET_DATE)

        quarters = self.get_argument("quarters", "")

        if quarters:
            quarters_array = quarters.split(',')

            if len(quarters_array) == 96:
                update_sheet(self.application.db, user_id, date, quarters)

                activities = get_activities(self.application.db, user_id)
                activity_dict = get_dict_from_sequence(activities, "id")
                summary, total = self._sheet_summary(quarters_array, activity_dict)
                self.write({ "summary" : summary, "total" : total })
                self.finish()
            else:
                self.respond_with_error(ERROR_NOT_96_QUARTERS)
        else:
            logging.warn("Could not extract quarters from PUT request")
            self.respond_with_error(ERROR_NO_QUARTERS)
