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

import logging
import storage
import tornado.database

class QuarterSettings(object):
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
        logging.info("Updating settings")
        settings = storage.get_settings(self.db)
        if settings:
            for row in settings:
                self.settings[row.name] = row.value
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

def create_default_config(path):
    """Create a quarterapp.conf file from the example config file"""
    import shutil, os.path
    target = os.path.join(path, 'quarterapp.conf')
    if os.path.exists(target):
        print('Cowardly refusing to overwrite configuration file')
    else:
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'resources', 'quarterapp.example.conf'), target)