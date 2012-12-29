#
#  Copyright (c) 2012 Markus Eliasson, http://www.quarterapp.com/
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

import tornado.database

def get_activities(db, username):
    """Get all activities for the given user

    @param db The database connection to use
    @param username The authenticated username to retrieve activities for
    """
    activities = db.query("SELECT * FROM quarterapp.activities WHERE username=%s;", username)
    if not activities:
        activities = []
    return activities
    

def add_activity(db, username, title, color):
    """Adds a new activity

    @param db The database connection to use
    @param username The authenticated username to associate the activity with
    @param title The activity's title
    @param color The activity's color value (hex)
    """
    return db.execute("INSERT INTO quarterapp.activities (username, title, color) VALUES(%s, %s, %s);", username, title, color)

def update_activity(db, username, activity_id, title, color):
    """Update an existing activity with new values

    @param db The database connection to use
    @param username The authenticated username the activity is associated with
    @oaram activity_id The id of the activity to update
    @param title The activity's title
    @param color The activity's color value (hex)
    """
    return db.execute("UPDATE quarterapp.activities SET title=%s, color=%s WHERE username=%s AND id=%s;", title, color, username, activity_id)

def delete_activity(db, username, activity_id):
    """Deletes a given activity

    @param db The database connection to use
    @param username The authenticated username the activity is associated with
    @oaram activity_id The id of the activity to delete
    """
    return db.execute("DELETE FROM quarterapp.activities WHERE username=%s AND id=%s;", username, activity_id)
