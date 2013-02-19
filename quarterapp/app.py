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
import logging
from collections import Counter

import tornado.web
from tornado.options import options
from tornado.web import HTTPError

from basehandlers import *
from api import BaseSheetHandler
from storage import *
from quarter_errors import *
from quarter_utils import *

class ActivityHandler(AuthenticatedHandler):
    @authenticated_user
    def get(self):
        user_id  = self.get_current_user_id()
        activities = get_activities(self.application.db, user_id)
        self.render(u"app/activities.html", activities = activities)

class SheetHandler(BaseSheetHandler):

    @authenticated_user
    def get(self, date = None):
        user_id  = self.get_current_user_id()
        date_obj = None
        today = datetime.date.today()

        if date:
            try:
                parts = date.split("-")
                if len(parts) != 3:
                    raise ValueErrror("Date should be in YYYY-MM-DD")
                else:
                    date_obj = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
            except:
                logging.warning("Could not verify date")
                raise HTTPError(500)
        else:
            date_obj = today

        yesterday = date_obj - datetime.timedelta(days = 1)
        tomorrow = date_obj + datetime.timedelta(days = 1)
        weekday = date_obj.strftime("%A")

        activities = get_activities(self.application.db, user_id)

        # Create a dict representation of the list of activities, to quicker resolve colors
        # for cells.
        activity_dict = get_dict_from_sequence(activities, "id")

        sheet = get_sheet(self.application.db, user_id, date_obj)
        
        quarters = []
        summary = []
        summary_total = "%.2f" %  0
        if sheet:
            ids = sheet.split(',')
            for i in ids:
                if int(i) > -1:
                    color = activity_dict[int(i)]["color"]
                    border_color = luminance_color(color, -0.2) # darken color
                    quarters.append({ "id" : i, "color" : color, "border-color" : border_color})
                else:
                    quarters.append({ "id" : i, "color" : "#fff", "border-color" : "#ccc"})
            
            summary, summary_total = self._sheet_summary(ids, activity_dict)
        else:
            quarters = self._default_sheet()
        
        self.render(u"app/sheet.html", date = date_obj, weekday = weekday,
            today = today, yesterday = yesterday, tomorrow = tomorrow,
            activities = activities, quarters = quarters, summary = summary, summary_total = summary_total)

class ProfileHandler(AuthenticatedHandler):
    @authenticated_user
    def get(self):
        user_id  = self.get_current_user_id()
        sheet_count = get_sheet_count(self.application.db, user_id)
        
        self.render(u"app/profile.html", sheet_count = sheet_count, error = None)

class DeleteAccountHandler(AuthenticatedHandler):
    @authenticated_user
    def post(self):
        password = self.get_argument("password", "")
        username = self.current_user["username"]
        user_id  = self.get_current_user_id()

        error = None
        if len(password) == 0:
            error = "not_valid"

        hashed_password = hash_password(password, username)
        authenticated = authenticate_user(self.application.db, username, hashed_password)
        if not authenticated:
            error = "not_valid"

        if error:
            sheet_count = get_sheet_count(self.application.db, user_id)
            self.render(u"app/profile.html", sheet_count = sheet_count, error = error)
        else:
            delete_user(self.application.db, username)
            self.set_current_user(None)
            self.redirect(u"/")
