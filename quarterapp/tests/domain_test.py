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

# Activity 6 : 0.75 h
# Activity 14:  5 h
a6_075h_a14_5h = ["-1","-1","-1","6","6","6","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "14","14","14","14","14","14","14","14","14","14",
    "14","14","14","14","14","14","14","14","14","14",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1","-1","-1","-1","-1",
    "-1","-1","-1","-1","-1","-1"]

class TestColor(unittest.TestCase):
    def test_create_color(self):
        color= Color("#fff")
        self.assertEqual("#fff", color.hex())

    @raises(InvalidColorError)
    def test_cannot_create_invalid_color(self):
        color= Color("banan")

    @raises(InvalidColorError)
    def test_cannot_create_empty_color(self):
        color= Color("")

    @raises(TypeError)
    def test_cannot_create_none_color(self):
        color= Color(None)
    
    def test_luminance_color(self):
        c1 = Color("#fff").luminance_color(0)
        c2 = Color("#fcaf3e").luminance_color(-0.25)
        c3 = Color("#fcaf3e").luminance_color(0.25)
        c4 = Color("#3465a4").luminance_color(0.66)
        self.assertEqual("#ffffff", c1.hex())
        self.assertEqual("#bd832f", c2.hex())
        self.assertEqual("#ffdb4e", c3.hex())
        self.assertEqual("#56a8ff", c4.hex())

class TestActivity(unittest.TestCase):
    def test_empty_activity(self):
        activity = Activity(1)
        self.assertEqual(0, activity.total())

    def test_activity_quarters(self):
        activity = Activity(1, 4)
        self.assertEqual(4, activity.total())

    def test_activity_color(self):
        activity = Activity(1, 3, color = Color("#cdcdcd"))
        self.assertEquals("#cdcdcd", activity.color.hex())

    def test_change_activity_color(self):
        activity = Activity(1, 3, color = Color("#cdcdcd"))
        self.assertEquals("#cdcdcd", activity.color.hex())
        activity.color = Color("#123123")
        self.assertEquals("#123123", activity.color.hex())

    def test_activity_has_default_title(self):
        activity = Activity(1)
        self.assertIsNotNone(activity.title)

    def test_can_change_activity_title(self):
        activity = Activity(1, title="Comet")
        self.assertEquals("Comet", activity.title)

        activity.title = "House"
        self.assertEquals("House", activity.title)        

class TestActivityDict(unittest.TestCase):
    def test_supports_string_as_key(self):
        the_list = []
        the_list.append(Activity(id="two", title="Activity 2"))
        the_list.append(Activity(id="three", title="Activity 3"))
        the_list.append(Activity(id="one", title="Activity 1"))

        the_dict = ActivityDict(the_list)
        self.assertEquals("Activity 1", the_dict["one"].title)
        self.assertEquals("two", the_dict["two"].id)

    def test_supports_int_as_key(self):
        the_list = []
        the_list.append(Activity(id=2, title="Activity 2"))
        the_list.append(Activity(id=3, title="Activity 3"))
        the_list.append(Activity(id=1, title="Activity 1"))

        the_dict = ActivityDict(the_list)
        self.assertEquals("Activity 1", the_dict[1].title)
        self.assertEquals(2, the_dict[2].id)

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

    def test_activities_are_sorted(self):
        sheet = Timesheet(datetime.today(), a3_075h_a7_5h_a39_15h)
        idx = 0
        for activity in sheet.activities:
            if idx == 0:
                self.assertEquals("3", activity.id)
            elif idx == 1:
                self.assertEquals("7", activity.id)
            elif idx == 2:
                self.assertEquals("39", activity.id)
            idx += 1

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

    def test_get_all_activities(self):
        week10 = Week(2013, 10)
        monday = Timesheet(date(2013, 03, 4), a3_075h_a7_5h_a39_15h)
        wednesday  = Timesheet(date(2013, 03, 6), a6_075h_a14_5h)

        week10.update_sheet(monday)
        week10.update_sheet(wednesday)
        
        unique_activities = week10.get_weeks_activities()
        self.assertEquals(5, len(unique_activities))


