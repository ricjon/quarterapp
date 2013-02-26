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

import unittest
import datetime

from nose.tools import raises

from quarterapp.domain import *

# Activity 3 : 0.75 h
a3_075h = ["-1","-1","-1","3","3","3","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1"]

# Activity 3 : 0.75 h
# Activity 7:  5 h
# Activity 39: 1.5 h
a3_075h_a7_5h_a39_15h = ["-1","-1","-1","3","3","3","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "7","7","7","7","7","7","7","7","7","7",
    "7","7","7","7","7","7","7","7","7","7",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","39","39","39","39","39","39","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1"]

a3_075h_a7_5h_a39_15h_str = "-1,-1,-1,3,3,3,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,39,39,39,39,39,39,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1"

class TestActivity(unittest.TestCase):
    def test_empty_activity(self):
        activity = Activity(1)
        self.assertEqual(0, activity.total())

    def test_activity_quarters(self):
        activity = Activity(1, 4)
        self.assertEqual(4, activity.total())

class TestTimesheet(unittest.TestCase):
    def test_timesheet(self):
        sheet = Timesheet(datetime.today())
        self.assertIsNotNone(sheet)

    def test_empty_timesheet(self):
        sheet = Timesheet(datetime.today())
        self.assertEquals(0, sheet.total())

    def test_small_sheet(self):
        sheet = Timesheet(datetime.today(), a3_075h)
        self.assertEqual(0.75, sheet.total())

    def test_complex_sheet_total(self):
        sheet = Timesheet(datetime.today(), a3_075h_a7_5h_a39_15h)
        self.assertEqual(7.25, sheet.total())

    def test_iterate_sheet(self):
        sheet = Timesheet(datetime.today(), a3_075h_a7_5h_a39_15h)

        activity_count = 0
        for activity in sheet:
            activity_count += 1

        self.assertEquals(3, activity_count)

    def test_sheet_activities(self):
        sheet = Timesheet(datetime.today(), a3_075h_a7_5h_a39_15h)
        self.assertEquals(1.5, sheet["39"].amount)
        self.assertEquals(5, sheet["7"].amount)

    def test_sheet_quarter_str(self):

        sheet = Timesheet(datetime.today(), a3_075h_a7_5h_a39_15h_str.split(","))
        self.assertEquals(1.5, sheet["39"].amount)
        self.assertEquals(5, sheet["7"].amount)

    def test_date_format(self):
        monday = Timesheet(date(2013, 02, 18))
        self.assertEquals("2013-02-18", monday.date_as_string())

class TestWeek(unittest.TestCase):
    def test_week(self):
        week8 = Week(2013, 8)
        self.assertIsNotNone(week8)
        self.assertEquals(7, len(week8.sheets))
        self.assertEquals(0, week8.total())

    def test_iterate_week(self):
        week8 = Week(2013, 8)

        counter = 0
        for day in week8:
            counter += 1

        # A week should always contain 7 sheets, even if they are empty
        self.assertEquals(7, counter)
