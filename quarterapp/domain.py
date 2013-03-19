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

from datetime import date, timedelta, datetime
from exceptions import Exception, OverflowError
from collections import Counter
import operator
import re
import math

color_hex_match_re = re.compile(r"^(#)([0-9a-fA-F]{3})([0-9a-fA-F]{3})?$")

class BaseError(Exception):
    def __init__(self, message):
        self.message = message

class NotFullDayError(BaseError):
    pass

class InvalidColorError(BaseError):
    pass

class User(object):
    """
    A quarter user
    """
    Normal=0
    Administrator=1
    Enabled = 1
    Disabled = 0

class ActivityDict(dict):
    """
    Creats a dictionary containing Activity objects using the id as key
    """
    def __init__(self, activity_list):
        for activity in activity_list:
            self[activity.id] = activity

class Color(object):
    """
    Represents a CSS color but only supports HEX format
    """
    def __init__(self, hex):
        """
        Creates a color object, will raise InvalidColorError if the
        given hex value is not correct.

        @param hex The hex value of this color
        @return A Color object
        """
        if not color_hex_match_re.match(hex):
            raise InvalidColorError("Not a valid HEX color code")
        self.hex_value = hex

    def hex(self):
        """
        Get the hex value for this color, will always be 4 or 7 chars (#fff or #cdcdcd)

        @return The colors HEX value
        """
        return self.hex_value

    def luminance_color(self, lum):
        """
        Create a new Color object with another luminance value. Use positive for lighter and
        negative to generate a darker color.

        @param lum Percentage luminance to alter. 
        @return A new Color object
        """
        color_code = self.hex_value.replace("#", "")
        lum = lum or 0;
        
        if len(color_code) == 3:
            color_code = color_code[0]+color_code[0]+color_code[1]+color_code[1]+color_code[2]+color_code[2]

        color = "#"
        for i in range(3):
            c = int(color_code[i * 2 : (i * 2) + 2], 16)
            c = int(round( min( max(0, c + (c * lum)), 255)))
            c = hex(c)[2:]
            color += str("00" + c)[len(c):]

        return Color(color)

    def __str__(self):
        return self.hex_value

class Week(object):
    """
    A week always contains 7 time sheets, no more no less.
    """

    def __init__(self, year, week):
        self.year = year
        self.week = week
        self.sheets = []
        self._create_default_sheets()
        
    def _create_default_sheets(self):
        first = self._week_start_date(self.year, self.week)
        for i in range(7):
            delta = timedelta(days = i)
            self.sheets.append(Timesheet(first  + delta))

    def _week_start_date(self, year, week):
        # From SO http://stackoverflow.com/a/1287862
        d = date(year, 1, 1)    
        delta_days = d.isoweekday() - 1
        delta_weeks = week
        if year == d.isocalendar()[0]:
            delta_weeks -= 1
        delta = timedelta(days=-delta_days, weeks=delta_weeks)
        return d + delta

    def total(self):
        """
        Get the total number of hours spent on any activity for this week

        @return The total number of hours this week
        """
        accumelator = 0
        for sheet in self.sheets:
            accumelator += sheet.total()
        return accumelator

    def update_sheet(self, sheet):
        """
        Updates the sheet with the given sheet
        """
        # TODO Check that sheet is within range
        self.sheets[sheet.weekday] = sheet

    def week_of_year(self):
        """
        Get the week of year for this week
        """
        return self.week

    def get_weeks_activities(self):
        """
        Get a sorted unique list of all the weeks activities where the
        activities amount is sumed up
        """
        all_activities = []
        unique_activities = []
        for sheet in self.sheets:
            all_activities += sheet.activities

        # Filter out any duplicates and merge the amount of time spent
        for aa in all_activities:
            matches = list((ua for ua in unique_activities if ua.id == aa.id))
            if len(matches) > 0:
                # Item already exist in list of unique activities
                # Mutable data, yay!
                updated_activity = Activity(aa.id, aa.amount + matches[0].amount)
                
                unique_activities.remove(matches[0])
                unique_activities.append(updated_activity)
            else:
                unique_activities.append(aa)

        # Sort on id
        unique_activities.sort(key = lambda x: int(x.id))
        return unique_activities


    # Built in python support
    def __iter__(self):
        return self.sheets.__iter__()

    def next(self):
        return self.sheets.next()

    def __str__(self):
        desc = "Week: %d\n" % self.week
        desc += "Sheets: \n"
        for sheet in self.sheets:
            desc += "\t%s\n" % sheet.date_as_string()
            for act in sheet:
                desc += "\t\t %s: %s\n" % (act.id, act.amount)
        return desc

class Timesheet(object):
    """
    A timesheet is the 96 quarters that constitutes a day. This class also contains
    utility functions for getting summarized info of activities spent on that day.

    If no quarters is given a default list of "No work" activities will be created

    The activities are always sorted ascending on id.

    Activities can be accessed by id using sheet[id]

    @param date The date for this weekday
    @param quarters An array of quarters containing the activity ids (must be 96)
    """
    
    def __init__(self, date, quarters=[]):
        if not quarters:
            quarters = []
        
        if len(quarters) != 0 and len(quarters) != 96:
            raise NotFullDayError("A timesheet must contain 96 quarters or none, not %d" % len(quarters))

        self.date = date
        self.weekday = date.weekday() # 0 based
        self.activities = [] # Summarized list of activities
        self.quarters = []
        self.iterator_index = 0
        self._create_sheet(quarters)
        self._summarize()
        
    def _create_sheet(self, quarters):
        if len(quarters) == 0 or quarters == None:
            for i in range(0, 96):
                self.quarters.append("-1")
        else:
            self.quarters = quarters

    def _summarize(self):
        """
        Summarize the quarters and create activities for the sums
        """
        summary = Counter(self.quarters)
        for aid in summary:
            if aid == "-1":
                continue
            self.activities.append(Activity(aid, float(summary[aid] / 4.0)))
        self.activities.sort(key = lambda x: int(x.id))

    def total(self):
        """
        Get the total number of hours worth of activities for this day
        """
        accumelator = 0
        for act in self.activities:
            accumelator += act.total()

        return accumelator

    def date_as_string(self):
        """
        Get this days date as a YYYY-MM-DD formatted string
        """
        return self.date.strftime("%Y-%m-%d")

    def time(self, activity_id):
        for activity in self.activities:
            if activity.id == activity_id:
                return activity.amount
        return 0

    # Iterator protocol
    def __iter__(self):
        return self.activities.__iter__()

    def next(self):
        return self.activities.next()

    #  protocol
    def __getitem__(self, activity_id):
        try:
            for activity in self.activities:
                if activity.id == activity_id:
                    return activity
        except KeyError:
            raise AttributeError(name)


class Activity(object):
    """
    Represents a time sheets activity, which is the sum in hours of all quarters for this
    activity for a given time sheet. I.e. if the user spent 8 quarters on activity X  this
    activitys sum is 2 (hours).

    An activity cannot be more than 24 hours (96 quarters)
    """
    # State value
    Enabled = 1
    Disabled = 0

    def __init__(self, id=id, amount=0.0, color=Color("#fff"), title="", state=0):
        self.id = id
        self.amount = amount
        self.color = color
        self.title = title
        self.state = state

    def total(self):
        """
        Get the total number of hours for this activity

        @return The total number of hours
        """
        return self.amount

    def disable(self):
        """
        Set the activity as disabled
        """
        self.state = Activity.Disabled

    def disabled(self):
        """
        Returns True if this activity is disabled
        
        @return True if this activity is disabled, else False
        """
        return self.state == Activity.Disabled

    def enable(self):
        """
        Set the activity as enabled
        """
        self.state = Activity.Enabled

    def enabled(self):
        """
        Returns True if this activity is enabled
        
        @return True if this activity is enabled, else False
        """
        return self.state == Activity.Enabled
