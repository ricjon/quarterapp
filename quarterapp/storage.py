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

class User:
    Normal=0
    Administrator=1
    Enabled = 1
    Disabled = 0

def get_user_count(db):
    """
    Get the total number of users (not pending users), regardless of their state of type.

    @return The number of users
    """
    count = db.query("SELECT COUNT(*) FROM quarterapp.users;")
    if len(count) > 0:
        return count[0]["COUNT(*)"]
    else:
        return 0

def get_users(db, start = 0, count = 50):
    """
    Get a list of user rows starting at the given position. If the start index is out of bounds
    an empty list will be returned. If there are as many users as the given 'count' the list will
    be filled with as many as there is.

    @param db The database connection
    @param start The start index in the user table (default is 0)
    @param count The number of users to receive (default is 50)
    """
    users = db.query("SELECT id, username, type, state, last_login FROM quarterapp.users ORDER BY id LIMIT %s, %s;", int(start), int(count))
    if not users:
        users = []
    return users

def add_user(db, username, password, user_type = User.Normal):
    """
    Adds a new user

    The username needs to be unique and the password will be stored as is (i.e. it should be hashed prior
        to this function).

    The username should be a valid email address.
    
    The user will be active by default.
    The user will be a normal user by default.

    @param db The database connection
    @param username The username
    @param password The users password
    """
    return db.execute("INSERT INTO quarterapp.users (username, password, type, state) VALUES(%s, %s, %s, \"1\");",
        username, password, user_type)

def username_unique(db, username):
    """
    Check if the given username is unique or not

    @param db The database connection to use
    @param username The username to check
    @return True if the username is not used, else False
    """
    users = db.query("SELECT username FROM quarterapp.users WHERE username=%s;", username)
    return len(users) < 1

def enable_user(db, username):
    """
    Set the given user as an active user - regardless of previous state

    @param db The database connection to use
    @param username The user to enable
    """
    return db.execute("UPDATE quarterapp.users SET state=%s WHERE username=%s;", User.Enabled, username) == 1

def disable_user(db, username):
    """
    Set the given user as an disabled user - regardless of previous state

    @param db The database connection to use
    @param username The user to disable
    """
    return db.execute("UPDATE quarterapp.users SET state=%s WHERE username=%s;", User.Disabled, username) == 1
    

def delete_user(db, username):
    """
    Delete a user from the system. All activities and quarters owned by this user will
    also be deleted.

    @param db The database connection to use
    @param username The user to delete
    """
    # TODO Make a transaction and also delete all activities and quarters!
    return db.execute("DELETE FROM quarterapp.users WHERE username=%s;", username)

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
    return db.execute("UPDATE quarterapp.activities SET title=%s, color=%s WHERE username=\"%s\" AND id=\"%s\";", title, color, username, activity_id)

def delete_activity(db, username, activity_id):
    """Deletes a given activity

    @param db The database connection to use
    @param username The authenticated username the activity is associated with
    @param activity_id The id of the activity to delete
    """
    return db.execute("DELETE FROM quarterapp.activities WHERE username=\"%s\" AND id=\"%s\";", username, activity_id)

