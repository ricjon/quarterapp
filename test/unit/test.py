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

import unittest
import tornado.database
import os
import sys

# Need to add the quarterapp root directory to enable imports
sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

import quarterapp.storage

# Test configuration
mysql_database = "quarterapp2"
mysql_host = "127.0.0.1:3306"
mysql_user = "quarterapp"
mysql_password = "quarterapp"

class TestStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = tornado.database.Connection(mysql_host, mysql_database, 
            mysql_user, mysql_password)

    @classmethod
    def tearDownClass(cls):
        cls.db.execute("TRUNCATE TABLE quarterapp.activities;")
        cls.db.execute("TRUNCATE TABLE quarterapp.users;")
        cls.db.close()

    def testCleanup(self):
        self.db.execute("DELETE FROM quarterapp.activities")
        self.db.execute("DELETE FROM quarterapp.users")

    #def test_no_users(self):
    #    self.assertEqual(0, quarterapp.storage.get_user_count(self.db))
    #    users = quarterapp.storage.get_users(self.db, 0, 10)
    #    self.assertEqual(0, len(users))

    def test_add_one_user(self):
        self.assertEqual(0, quarterapp.storage.get_user_count(self.db))
        quarterapp.storage.add_user(self.db, username = "bob@example.com", password="secret")
        self.assertEqual(1, quarterapp.storage.get_user_count(self.db))

    def testNoActivities(self):
        activities = quarterapp.storage.get_activities(self.db, "bob@example.com")
        self.assertEqual(0, len(activities))

    def testAddActivity(self):
        quarterapp.storage.add_activity(self.db, "bob@example.com", "activity 1", "#ffffff")
        activities = quarterapp.storage.get_activities(self.db, "bob@example.com")
        self.assertEqual(1, len(activities))

    def testAddAnotherActivity(self):
        quarterapp.storage.add_activity(self.db, "bob@example.com", "activity 2", "#000")
        activities = quarterapp.storage.get_activities(self.db, "bob@example.com")
        self.assertEqual(2, len(activities))

if __name__ == "__main__":
    unittest.main()
