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

import logging
import storage
import tornado.database

class QuarterSettings:
    """
    Application settings contains the settings specific to the application,
    not the running server. I.e. port numbers and such should not be kept here
    but in the application configuration file (quarterapp.conf).

    These settings might be updated at runtime
    """

    def __init__(self, db):
        """
        Constructs the application settings and try to update the settings
        from database

        @param db The Tornado database object used to access the database
        """
        self.db = db
        self.settings = {}
        self.update()

    def update(self):
        """
        Update the settings from the database, if cannot read from database the
        old settings remain active
        """
        settings = storage.get_settings(self.db)
        if settings:
            for row in settings:
                self.settings[row.key] = row.value
        else:
            logging.warn("Could not find any settings in database - everything setup ok?")

    def get_value(self, key):
        """
        Get the setting value for the given key, if no setting exist for this key
        None is returned
        """
        if self.settings.has_key(key):
            return self.settings[key]
        else:
            return None

    def put_value(self, key, value):
        """
        Updates the value for the given key. If this key does not exist to begin with
        this function will not insert the value. I.e. this function will only update
        existing values.

        @param key The settings key to update value for
        @param value The new value
        """
        if self.settings.has_key(key):
            storage.put_setting(self.db, key, value)
            self.settings[key] = value
        else:
            logging.warning("Trying to update a settings key that does not exists! (%s)", key)
            raise Exception("Trying to update a settings key that does not exists!")
