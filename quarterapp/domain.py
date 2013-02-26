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

from datetime import date, timedelta, datetime
from exceptions import Exception, OverflowError
from collections import Counter

class BaseError(Exception):
    def __init__(self, message):
        self.message = message

class NotFullDayError(BaseError):
    pass

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
                desc += "\t\t %s: %s" % (act.id, act.amount)
        return desc

class Timesheet(object):
    """
    A timesheet is the 96 quarters that constitutes a day. This class also contains
    utility functions for getting summarized info of activities spent on that day.

    If no quarters is given a default list of "No work" activities will be created

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

    def __init__(self, id, amount=0.0):
        self.id = id
        self.amount = amount

    def total(self):
        """
        Get the total number of hours for this activity

        @return The total number of hours
        """
        return self.amount

