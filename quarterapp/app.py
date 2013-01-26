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
import tornado.web

from tornado.options import options
from tornado.web import HTTPError

from quarterapp.basehandlers import *
from quarterapp.storage import *
from quarterapp.errors import *

class IndexHandler(BaseHandler):
    def get(self):
        self.render(u"public/index.html")

class ActivityHandler(AuthenticatedHandler):
    @authenticated_user
    def get(self):
        user_id  = self.get_current_user_id()
        if not user_id:
            logging.error("Could not retrieve usr id")
            raise HTTPError(500)

        activities = None
        activities = get_activities(self.application.db, user_id)
        self.render(u"app/activities.html", activities = activities)

class SheetHandler(AuthenticatedHandler):
    @authenticated_user
    def get(self, date = None):
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
        self.render(u"app/sheet.html", date = date_obj, weekday = weekday,
            today = today, yesterday = yesterday, tomorrow = tomorrow)
