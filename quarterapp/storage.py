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

from functools import wraps
import sqlite3, re
_SQLITE_RE = re.compile(r'%\((\w+)\)s')

class User(object):
    Normal=0
    Administrator=1
    Enabled = 1
    Disabled = 0


class Data(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

def hack_sql(fn):
    """Hack MySQL driver SQL into SQLite3 driver SQL. 
    WISHLIST: Should have zero impact when using MySQL."""
    @wraps(fn)
    def hack_sql(db, sql, *args, **kwargs): 
        if isinstance(db, sqlite3.Connection):
            sql = _SQLITE_RE.sub(r':\1', sql.replace('%s', '?'))
        return fn(db, sql, *args, **kwargs)
    return hack_sql

@hack_sql
def _query(db, sql, *params):
    cursor = db.cursor()
    cursor.execute(sql, *params)
    cols = [c[0] for c in cursor.description]
    return [Data(zip(cols, row)) for row in cursor.fetchall()]

@hack_sql
def _query_rowcount(db, sql, params):
    cursor = db.cursor()
    cursor.execute(sql, params)
    
    return cursor.rowcount

@hack_sql
def _exec(db, sql, *params):
    cursor = db.cursor()
    cursor.execute(sql, *params)
    return cursor.lastrowid

def get_settings(db):
    """
    Get all settings from the database

    @param db The database connection
    @return a list of toupes (key / value)
    """
    return _query(db, "SELECT * FROM settings;", tuple())

def get_setting(db, name):
    """
    Get a specific setting

    @param db The database connection
    @param name The setting's name
    @return The setting's value
    """
    result = _query(db, "SELECT value FROM settings WHERE name=%(name)s;", { "name" : name })
    if len(result) > 0:
        return getattr(result[0], "value")
    return None

def put_setting(db, name, value):
    """
    Set a specific setting to the given value

    @param db The database connection
    @param name The setting's name
    @param value The setting's value
    @return True on success, else False
    """
    return _exec(db, "UPDATE settings SET value=%(value)s WHERE name=%(name)s ;", { "value" : value, "name" : name }) == 1

def get_signup_count(db):
    """
    Get the total number of pending users (signed up, not active)

    @param db The database connection
    @return The number of users
    """
    count = _query(db, "SELECT COUNT(*) FROM signups;")
    if len(count) > 0:
        return getattr(count[0], "COUNT(*)")
    else:
        return 0

def get_user_count(db):
    """
    Get the total number of users (not pending users), regardless of their state of type.

    @param db The database connection
    @return The number of users
    """
    count = _query(db, "SELECT COUNT(*) FROM users;")
    if len(count) > 0:
        return getattr(count[0], "COUNT(*)")
    else:
        return 0

def get_filtered_user_count(db, query_filter):
    """
    Get the total number of users (not pending users), regardless of their state of type, but
    filter the user based on a their usernames.

    @param db The database connection
    @param query_filter The filter to match against username
    @return The number of users
    """
    query_filter = "%{0}%".format(query_filter) # MySQL formatting using % as wildcard
    count = _query(db, "SELECT COUNT(*) FROM users WHERE username LIKE %(filter)s;", { "filter" : query_filter })
    if len(count) > 0:
        return getattr(count[0], "COUNT(*)")
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
    @return The list of users
    """
    users = _query(db, "SELECT id, username, type, state, last_login FROM users ORDER BY id LIMIT %(start)s, %(count)s;",
        { "start" : start, "count" : count })
    if not users:
        users = []
    return users

def get_filtered_users(db, query_filter, start = 0, count = 50):
    """
    Get a filtered list of user rows starting at the given position. If the start index is out of bounds
    an empty list will be returned. If there are as many users as the given 'count' the list will
    be filled with as many as there is.


    @param db The database connection
    @param query_filter The query filter to use
    @param start The start index in the user table (default is 0)
    @param count The number of users to receive (default is 50)
    @return A list of matched users
    """
    query_filter = "%{0}%".format(query_filter) # MySQL formatting using % as wildcard
    users = _query(db, "SELECT id, username, type, state, last_login FROM users WHERE username LIKE %(filter)s ORDER BY id LIMIT %(start)s, %(count)s;",
        { "filter" : query_filter, "start" : start, "count" : count })
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
    @returun True if the user was added else false
    """
    rowid = _exec(db, "INSERT INTO users (username, password, type, state) VALUES(%(username)s, %(password)s, %(user_type)s, \"1\");",
        { "username" : username, "password" : password, "user_type" : user_type })
    return rowid > -1

def username_unique(db, username):
    """
    Check if the given username is unique or not

    @param db The database connection to use
    @param username The username to check
    @return True if the username is not used, else False
    """
    users = _query(db, "SELECT username FROM users WHERE username=%(username)s;", {'username': username})
    return len(users) < 1

def enabled_user(db, username):
    """
    Check if the given user is enabled

    @param db The database connection to use
    @param username The user to check
    @return True if the user is enabled, else False (user is disabled)
    """
    users = _query(db, "SELECT state FROM users WHERE username=%(username)s;", { "username" : username })
    if len(users) > 0:
        return users[0].state == User.Enabled
    return False


def enable_user(db, username):
    """
    Set the given user as an active user - regardless of previous state

    @param db The database connection to use
    @param username The user to enable
    """
    _exec(db, "UPDATE users SET state=%(state)s WHERE username=%(username)s;", { "state" : User.Enabled, "username" : username })

def disable_user(db, username):
    """
    Set the given user as an disabled user - regardless of previous state

    @param db The database connection to use
    @param username The user to disable
    """
    _exec(db, "UPDATE users SET state=%(state)s WHERE username=%(username)s;", { "state" : User.Disabled, "username" : username })

def delete_user(db, username):
    """
    Delete a user from the system. All activities and quarters owned by this user will
    also be deleted.

    @param db The database connection to use
    @param username The user to delete
    """
    # TODO Make a transaction and also delete all activities and quarters!
    _exec(db, "DELETE FROM users WHERE username=%(username)s;", { "username" : username })

def signup_user(db, email, code, ip):
    """
    Add the given signup details

    @param db The database connection to use
    @param email The new users email
    @param code The activation code
    @param ip The IP address that requested the sign up
    @return True on success, else False 
    """
    # TODO Make transaction to see if username is unique
    rowid = _exec(db, "INSERT INTO signups (username, activation_code, ip) VALUES(%(email)s, %(code)s, %(ip)s);",
        { "email" : email, "code" : code, "ip" : ip })
    return rowid > -1

def activate_user(db, code, password):
    """
    Creates a new user if the given email is found in the signup table and the code matches the assigned
    activation code.

    A standard user is created.

    @param db The database connection to use
    @param code The activation code
    @param password The users encrypted password
    @return True if the user was activated, else False
    """
    try:
        # TODO Make transaction
        signups = _query(db, "SELECT username, activation_code FROM signups WHERE activation_code=%(code)s;", { "code" : code })

        if signups[0].activation_code == code:
            _exec(db, "DELETE FROM signups WHERE activation_code=%(code)s;", { 'code' : code })
            _exec(db, "INSERT INTO users (username, password, type, state) VALUES(%(username)s, %(password)s, \"0\", \"1\");",
                { "username": signups[0].username, "password" : password })
            return True
    except:
        return False

def set_user_reset_code(db, username, reset_code):
    """
    Set the reset code for a given user.

    @param db The database connection to use
    @param username The user to update
    @param reset_code The reset code to store
    @return True on success, else False
    """
    try:
        _exec(db, "UPDATE users SET reset_code=%(code)s WHERE username=%(user)s", { "code" : reset_code, "user" : username} )
        return True
    except:
        return False

def reset_password(db, reset_code, new_password):
    """
    Resets a user password for the user account with the given reset_code.

    @param db The database connection to use
    @param reset_code The unique reset code
    @param new_password The password to set (will not be hashed)
    @return True on success, else False
    """
    try:
        users = _query(db, "SELECT username FROM users WHERE reset_code=%(code)s;", { "code" : reset_code })
        if len(users) == 1:
            _exec(db, "UPDATE users SET password=%(newpass)s WHERE reset_code=%(code)s;", { "code" : reset_code, "newpass" : new_password })
            _exec(db, "UPDATE users SET reset_code='' WHERE reset_code=%(code)s;", { "code" : reset_code })
            return True
        else:
            return False
    except:
        return False

def authenticate_user(db, username, password):
    """
    Authenticates the given user

    @param db The database connection to use
    @param username The username to authenticate
    @param password The password hash to compare
    @return The user object (except the password)
    """
    try:
        users = _query(db, "SELECT id, username, type, state FROM users WHERE username=%(username)s AND password=%(password)s;",
            { "username" : username, "password" : password })
        if len(users) == 1:
            return users[0]
        else:
            return None
    except:
        return None

def get_activities(db, user_id):
    """
    Get all activities for the given user

    @param db The database connection to use
    @param user_id The id of the authenticated username to retrieve activities for
    """
    activities = _query(db, "SELECT id, title, color FROM activities WHERE user=%(user)s;", { "user" : user_id })
    if not activities:
        activities = []
    return activities    

def add_activity(db, user_id, title, color):
    """
    Adds a new activity

    @param db The database connection to use
    @param user_id The id of the authenticated user to associate the activity with
    @param title The activity's title
    @param color The activity's color value (hex)
    """
    return _exec(db, "INSERT INTO activities (user, title, color) VALUES(%(id)s, %(title)s, %(color)s);",
        { "id" : user_id, "title" : title, "color" : color })

def get_activity(db, user_id, activity_id):
    """
    Get the given activity_id
    @param db The database connection to use
    @param user_id The id of the authenticated user to associate the activity with
    @param activity_id The id of the activity to retrieve
    """
    activities = _query(db, "SELECT id, title, color FROM activities WHERE user=%(user)s AND id=%(activity_id)s;",
        { "user" : user_id, "activity_id" : activity_id })
    if activities and len(activities) == 1:
        return activities[0]
    else:
        return None

def update_activity(db, user_id, activity_id, title, color):
    """Update an existing activity with new values

    @param db The database connection to use
    @param user_id The id of the authenticated user to associate the activity with
    @oaram activity_id The id of the activity to update
    @param title The activity's title
    @param color The activity's color value (hex)
    """
    return _exec(db, "UPDATE activities SET title=%(title)s, color=%(color)s WHERE user=%(user)s AND id=%(activity_id)s;",
        { "title" : title, "color" : color, "user" : user_id, "activity_id" : activity_id})

def delete_activity(db, user_id, activity_id):
    """Deletes a given activity

    @param db The database connection to use
    @param user_id The id of the authenticated user the activity is associated with
    @param activity_id The id of the activity to delete
    """
    return _exec(db, "DELETE FROM activities WHERE user=%(user)s AND id=%(activity)s;", {'user': user_id, 'activity': activity_id})

def update_sheet(db, user_id, date, quarters):
    """
    Inserts the given time sheet for the given date. If a record exist for this
    date it will be replaced, if nothing exists a new record will be created.

    @param db The database connection to use
    @param user_id The id of the authenticated user the activity is associated with
    @param date The time sheets date, must be in the format YYYY-MM-DD
    @param quarters the time sheets list of quarters
    """
    result = _query_rowcount(db, "UPDATE sheets SET quarters=%(quarters)s WHERE user=%(user)s and date=%(date)s",
        { "quarters" : quarters, "user" : user_id, "date" : date })
    if result == 0:
        result = _exec(db, "INSERT INTO sheets (user, date, quarters) VALUES(%(user)s, %(date)s, %(quarters)s);",
            { "quarters" : quarters, "user" : user_id, "date" : date })
    return result

def get_sheet(db, user_id, date):
    """
    Get a timesheet for the given user and date

    @param db The database connection to use
    @param user_id The id of the authenticated user the activity is associated with
    @param date The time sheets date, must be in the format YYYY-MM-DD
    @return The sheet containing the quarters or None if no sheet found
    """
    sheets = _query(db, "SELECT quarters FROM sheets WHERE user=%(user)s and date=%(date)s", { "user" : user_id, "date" : date })
    if sheets and len(sheets) == 1:
        return sheets[0]["quarters"]
    else:
        return None
