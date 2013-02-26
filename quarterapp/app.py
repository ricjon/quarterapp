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
from domain import Timesheet, Week

class ActivityHandler(AuthenticatedHandler):
    @authenticated_user
    def get(self):
        user_id  = self.get_current_user_id()
        activities = get_activities(self.application.db, user_id)
        self.render(u"app/activities.html", options = options, activities = activities)

class SheetHandler(BaseSheetHandler):
    @authenticated_user
    def get(self, sheet_date = None):
        user_id  = self.get_current_user_id()
        date_obj = None
        today = datetime.date.today()

        if sheet_date:
            if valid_date(sheet_date):
                date_obj = extract_date(sheet_date)
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
        
        self.render(u"app/sheet.html", options = options, date = date_obj, weekday = weekday,
            today = today, yesterday = yesterday, tomorrow = tomorrow,
            activities = activities, quarters = quarters, summary = summary, summary_total = summary_total)

class ProfileHandler(AuthenticatedHandler):
    @authenticated_user
    def get(self):
        user_id  = self.get_current_user_id()
        sheet_count = get_sheet_count(self.application.db, user_id)
        
        self.render(u"app/profile.html", options = options, sheet_count = sheet_count, error = None)

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
            self.render(u"app/profile.html", options = options, sheet_count = sheet_count, error = error)
        else:
            delete_user(self.application.db, username)
            self.set_current_user(None)
            self.redirect(u"/")

class ReportHandler(AuthenticatedHandler):
    @authenticated_user
    def get(self):
        self.render(u"app/report.html", options = options, start = None, end = None, error = None, weeks = None)

    def post(self):
        start = self.get_argument("start-date", "")
        end = self.get_argument("end-date", "")
        user_id  = self.get_current_user_id()

        start_date = extract_date(start)
        end_date = extract_date(end)

        error = None
        if not start_date:
            error = "start_date_not_valid"
        elif not end_date:
            error = "end_date_not_valid"
        elif start_date >= end_date:
            error = "end_date_not_later"

        # Report algorithm
        weeks = []
        start_week = start_date.isocalendar()[1]
        end_week = end_date.isocalendar()[1]
        for i in range(start_week, end_week+1):
            year = start_date.year

            if end_week < start_week: # Report from dec -> jan
                year = end_date.year

            week = Week(year, i)
            for blank_sheet in week:
                # TODO Make get_sheet return instance of Sheet
                quarters = get_sheet(self.application.db, user_id, blank_sheet.date_as_string())
                sheet = Timesheet(blank_sheet.date, quarters.split(",") if quarters else [])
                week.update_sheet(sheet)
            
            weeks.append(week)

        #for week in weeks:
        #    print week

        self.render(u"app/report.html", options = options, start = start, end = end, error = error, weeks = weeks)
