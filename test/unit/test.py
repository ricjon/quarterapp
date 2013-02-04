#
#  Copyright (c) 2012-2013 Markus Eliasson, http://www.quarterapp.com/
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
import tornado.database
import os
import sys

# Need to add the quarterapp root directory to enable imports
sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

import quarterapp.storage
from quarterapp.utils import *

# Test configuration
mysql_database = "quarterapp_test"
mysql_host = "127.0.0.1:3306"
mysql_user = "quarterapp"
mysql_password = "quarterapp"

BOB_THE_USER = 1

def default_sheet():
    quarters = []
    for i in range(0, 96):
        quarters.append(-1)
    return quarters

class TestUnit(unittest.TestCase):
    def test_hex(self):
        self.assertTrue(valid_color_hex("#fff"))
        self.assertTrue(valid_color_hex("#ffffff"))
        self.assertTrue(valid_color_hex("#000"))
        self.assertTrue(valid_color_hex("#123456"))
        
        self.assertFalse(valid_color_hex("fff"))
        self.assertFalse(valid_color_hex("cdcdcd"))
        self.assertFalse(valid_color_hex("#ggg"))
        self.assertFalse(valid_color_hex("#cccc"))
        self.assertFalse(valid_color_hex("0"))
        self.assertFalse(valid_color_hex(""))

    def test_hash_password(self):
        self.assertEqual( 88, len(hash_password("secret", "salt")) )
        self.assertEqual( 88, len(hash_password("anothersecret", "salt")) )
        self.assertEqual( hash_password("secret", "salt"), hash_password("secret", "salt"))
        self.assertNotEqual( hash_password("secret", "salt"), hash_password("secret", "pepper"))

    def test_valid_date(self):
        self.assertTrue(valid_date("2013-01-29"))
        self.assertTrue(valid_date("1999-12-29"))
        self.assertTrue(valid_date("2013-11-01"))
        self.assertTrue(valid_date("2012-02-29"))

        self.assertFalse(valid_date("2013-29-11"))
        self.assertFalse(valid_date("2013-9-1"))
        self.assertFalse(valid_date("2013-02-29"))
        self.assertFalse(valid_date("13-1-29"))
        self.assertFalse(valid_date("29/01/2013"))
        self.assertFalse(valid_date("01/29/2013"))

class TestStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = tornado.database.Connection(mysql_host, mysql_database, 
            mysql_user, mysql_password)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def tearDown(self):
        self.db.execute("TRUNCATE TABLE " + self.db.database + ".activities;")
        self.db.execute("TRUNCATE TABLE " + self.db.database + ".users;")

    def test_cleanup(self):
        self.db.execute("DELETE FROM " + self.db.database + ".activities")
        self.db.execute("DELETE FROM " + self.db.database + ".users")
        self.db.execute("DELETE FROM " + self.db.database + ".sheets")

    def test_no_activities(self):
        activities = quarterapp.storage.get_activities(self.db, BOB_THE_USER)
        self.assertEqual(0, len(activities))

    def test_add_activity(self):
        quarterapp.storage.add_activity(self.db, BOB_THE_USER, "activity 1", "#ffffff")
        activities = quarterapp.storage.get_activities(self.db, BOB_THE_USER)
        self.assertEqual(1, len(activities))

    def test_get_activity(self):
        activity_id = quarterapp.storage.add_activity(self.db, BOB_THE_USER, "Activity 2", "#ccc")
        activity = quarterapp.storage.get_activity(self.db, BOB_THE_USER, activity_id)
        self.assertEqual(activity.title, "Activity 2")

    def test_delete_activity(self):
        activity_id = quarterapp.storage.add_activity(self.db, BOB_THE_USER, "Activity 3", "#123123")
        activity = quarterapp.storage.get_activity(self.db, BOB_THE_USER, activity_id)
        self.assertIsNotNone(activity)

        quarterapp.storage.delete_activity(self.db, BOB_THE_USER, activity_id)
        activity = quarterapp.storage.get_activity(self.db, BOB_THE_USER, activity_id)
        self.assertIsNone(activity)

    def test_get_activity(self):
        activity_id = quarterapp.storage.add_activity(self.db, BOB_THE_USER, "Activity 444", "#ccc")
        activity = quarterapp.storage.get_activity(self.db, BOB_THE_USER, activity_id)
        self.assertEqual(activity.title, "Activity 444")

        quarterapp.storage.update_activity(self.db, BOB_THE_USER, activity_id, "Activity 4", activity.color)
        activity = quarterapp.storage.get_activity(self.db, BOB_THE_USER, activity_id)
        self.assertEqual(activity.title, "Activity 4")
        self.assertEqual(activity.color, "#ccc")

    def test_get_empty_sheet(self):
        sheet = quarterapp.storage.get_sheet(self.db, BOB_THE_USER, "2013-02-05")
        self.assertIsNone(sheet)

    def test_update_sheet(self):
        sheet = quarterapp.storage.get_sheet(self.db, BOB_THE_USER, "2013-02-05")
        self.assertIsNone(sheet)

        quarterapp.storage.update_sheet(self.db, BOB_THE_USER, "2012-02-05", str(default_sheet()))
        sheet = quarterapp.storage.get_sheet(self.db, BOB_THE_USER, "2012-02-05")
        
        sself.assertIsNotNone(sheet)

if __name__ == "__main__":
    unittest.main()
