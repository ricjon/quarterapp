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
            update_activity(self.application.db, user_id, activity_id, title, color)
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
