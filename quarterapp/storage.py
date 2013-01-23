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

def get_signup_count(db):
    """
    Get the total number of pending users (signed up, not active)

    @return The number of users
    """
    count = db.query("SELECT COUNT(*) FROM quarterapp.signups;")
    if len(count) > 0:
        return count[0]["COUNT(*)"]
    else:
        return 0

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

def get_filtered_user_count(db, query_filter):
    query_filter = "%{0}%".format(query_filter) # MySQL formatting using % as wildcard
    count = db.query("SELECT COUNT(*) FROM quarterapp.users WHERE username LIKE %s;", query_filter)
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

def get_filtered_users(db, query_filter, start = 0, count = 50):
    query_filter = "%{0}%".format(query_filter) # MySQL formatting using % as wildcard
    users = db.query("SELECT id, username, type, state, last_login FROM quarterapp.users WHERE username LIKE %s ORDER BY id LIMIT %s, %s;", query_filter, int(start), int(count))
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

def signup_user(db, email, code, ip):
    # TODO Make transaction to see if username is unique
    return db.execute("INSERT INTO quarterapp.signups (username, activation_code, ip) VALUES(%s, %s, %s);",
        email, code, ip)

def activate_user(db, code, password):
    """
    Creates a new user if the given email is found in the signup table and the code matches the assigned
    activation code.

    A standard user is created.

    """
    try:
        # TODO Make transaction
        signups = db.query("SELECT username, activation_code FROM quarterapp.signups WHERE activation_code=%s;", code)

        if signups[0]["activation_code"] == code:
            db.execute("DELETE FROM quarterapp.signups WHERE activation_code=%s;", code)
            db.execute("INSERT INTO quarterapp.users (username, password, type, state) VALUES(%s, %s, \"0\", \"1\");", signups[0]["username"], password)
            return True
    except:
        return False

def set_user_reset_code(db, username, reset_code):
    """
    Set the reset code for a given user.

    @param db The database connection to use
    @param username The user to update
    @param reset_code The reset code to store
    """
    try:
        db.execute("UPDATE quarterapp.users SET reset_code=%s WHERE username=%s;", reset_code, username)
        return True
    except:
        return False

def reset_password(db, reset_code, new_password):
    """
    Resets a user password for the user account with the given reset_code.

    @param db The database connection to use
    @param reset_code The unique reset code
    @param new_password The password to set (will not be hashed)
    """
    try:
        users = db.query("SELECT username FROM quarterapp.users WHERE reset_code=%s;", reset_code)
        if len(users) == 1:
            db.execute("UPDATE quarterapp.users SET password=%s WHERE reset_code=%s;", new_password, reset_code)
            db.execute("UPDATE quarterapp.users SET reset_code='' WHERE reset_code=%s;", reset_code)
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
        users = db.query("SELECT id, username, type, state FROM quarterapp.users WHERE username=%s AND password=%s;", username, password)
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
    activities = db.query("SELECT id, title, color FROM quarterapp.activities WHERE user=%s;", user_id)
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
    return db.execute("INSERT INTO quarterapp.activities (user, title, color) VALUES(%s, %s, %s);", user_id, title, color)

def get_activity(db, user_id, activity_id):
    """
    Get the given activity_id
    @param db The database connection to use
    @param user_id The id of the authenticated user to associate the activity with
    @param activity_id The id of the activity to retrieve
    """
    activities = db.query("SELECT id, title, color FROM quarterapp.activities WHERE user=%s AND id=%s;", user_id, activity_id)
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
    return db.execute("UPDATE quarterapp.activities SET title=%s, color=%s WHERE user=%s AND id=%s;", title, color, user_id, activity_id)

def delete_activity(db, user_id, activity_id):
    """Deletes a given activity

    @param db The database connection to use
    @param user_id The id of the authenticated user the activity is associated with
    @param activity_id The id of the activity to delete
    """
    return db.execute("DELETE FROM quarterapp.activities WHERE user=%s AND id=%s;", user_id, activity_id)

