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

import unittest
import sqlite3
import os
import sys
import tempfile

import quarterapp.storage
from quarterapp.settings import *
from quarterapp.quarter_utils import *

#
# Test can be run using either SQLite or MySQL as database. By default
# SQLite is used, but changing this to True and filling the details in the 
# MYSQL_TEST_CONFIG dict will make you run on MySQL instead.
USE_MYSQL = True

MYSQL_TEST_CONFIG = {
    "database" : "quarterapp_test",
    "host" : "127.0.0.1",
    "port" : 3306,
    "user" : "quarterapp",
    "password" : "quarterapp"}


def setup_sqlite(filename):
    conn = sqlite3.connect(filename)

    sql = """
    CREATE TABLE `activities` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `user` INT(11) NOT NULL,
    `title` VARCHAR(32) NOT NULL DEFAULT '',
    `color` VARCHAR(32) NOT NULL DEFAULT ''
);

CREATE TABLE `sheets` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `user` INT(11) NOT NULL,
    `date` DATE NOT NULL,
    `quarters` TEXT NOT NULL
) ;

CREATE TABLE `settings` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` VARCHAR(64) NOT NULL UNIQUE,
    `value` TEXT NOT NULL
    
);

CREATE TABLE `users` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `username` VARCHAR(256) NOT NULL DEFAULT '',
    `password` VARCHAR(90) NOT NULL DEFAULT '',
    `salt` VARCHAR(256) NOT NULL DEFAULT '',
    `type` TINYINT NOT NULL DEFAULT '0',
    `state`  TINYINT NOT NULL DEFAULT '0',
    `last_login` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `reset_code` VARCHAR(64)
) ;

CREATE TABLE `signups` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `username` VARCHAR(256) NOT NULL DEFAULT '',
    `activation_code` VARCHAR(64) NOT NULL DEFAULT '',
    `ip` VARCHAR(39) NOT NULL DEFAULT '',
    `signup_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO settings (`name`, `value`) VALUES("allow-signups", "1");
INSERT INTO settings (`name`, `value`) VALUES("allow-activations", "1");

INSERT INTO users (`username`, `password`, `type`, `state`) VALUES("admin", "", 1, 1);"""
    cur = conn.cursor()
    for stmt in sql.split(';'):
        try:
            cur.execute(stmt)
        except:
            print("Exception when executing '" + stmt + "'")
            raise
    return conn

# Test data
BOB_THE_USER = 1

# A default, bland time sheet
def default_sheet():
    quarters = []
    for i in range(0, 96):
        quarters.append(-1)
    return quarters

class TestStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if USE_MYSQL:
            import MySQLdb
            cls.db = MySQLdb.connect(host = MYSQL_TEST_CONFIG["host"], port =  MYSQL_TEST_CONFIG["port"],
                db = MYSQL_TEST_CONFIG["database"], user = MYSQL_TEST_CONFIG["user"], passwd = MYSQL_TEST_CONFIG["password"])
        else:
            fd, temp_name = tempfile.mkstemp()
            os.close(fd) #Don't need the fd
            cls.db = setup_sqlite(temp_name)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def tearDown(self):
        quarterapp.storage._exec(self.db, "DELETE FROM activities")
        quarterapp.storage._exec(self.db, "DELETE FROM users")
        quarterapp.storage._exec(self.db, "DELETE FROM sheets")

    ## Activities test

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


    ## Sheet test

    def test_get_empty_sheet(self):
        sheet = quarterapp.storage.get_sheet(self.db, BOB_THE_USER, "2013-02-05")
        self.assertIsNone(sheet)

    def test_update_sheet(self):
        sheet = quarterapp.storage.get_sheet(self.db, BOB_THE_USER, "2013-02-05")
        self.assertIsNone(sheet)

        quarterapp.storage.update_sheet(self.db, BOB_THE_USER, "2012-02-05", str(default_sheet()))
        sheet = quarterapp.storage.get_sheet(self.db, BOB_THE_USER, "2012-02-05")
        
        self.assertIsNotNone(sheet)


    ## Signup tests

    def test_signup_user(self):
        result = quarterapp.storage.signup_user(self.db, "one@example.com", "sleepy", "localhost")
        self.assertTrue(result)

    def test_user_activation_fails(self):
        result = quarterapp.storage.signup_user(self.db, "one@example.com", "sleepy", "127.0.0.1")
        self.assertTrue(result)

        result = quarterapp.storage.activate_user(self.db, "tired", "mybloodyvalentine", "salt")
        self.assertFalse(result)

    def test_user_activation_success(self):
        result = quarterapp.storage.signup_user(self.db, "one@example.com", "sleepy", "127.0.0.1")
        self.assertTrue(result)

        result = quarterapp.storage.activate_user(self.db, "sleepy", "mybloodyvalentine", "salt")
        self.assertTrue(result)

    def test_many_signups(self):
        quarterapp.storage.signup_user(self.db, "one@example.com", "sleepy", "127.0.0.1")
        quarterapp.storage.signup_user(self.db, "two@example.com", "sleepy", "127.0.0.1")
        quarterapp.storage.signup_user(self.db, "three@example.com", "sleepy", "127.0.0.1")
        quarterapp.storage.signup_user(self.db, "four@example.com", "sleepy", "127.0.0.1")

        result = quarterapp.storage.get_signup_count(self.db)
        self.assertEqual(4, result)

    def test_update_signup(self):
        result = quarterapp.storage.signup_user(self.db, "one@example.com", "dopey", "127.0.0.1")
        self.assertTrue(result)

        result = quarterapp.storage.signup_user(self.db, "one@example.com", "grumpy", "127.0.0.1")
        self.assertTrue(result)

        result = quarterapp.storage.activate_user(self.db, "dopey", "mybloodyvalentine", "salt")
        self.assertFalse(result)

        result = quarterapp.storage.activate_user(self.db, "grumpy", "mybloodyvalentine", "salt")
        self.assertTrue(result)


    ## User test

    def test_add_users(self):
        result = quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        self.assertTrue(result)
        result = quarterapp.storage.add_user(self.db, "bobby@example.com", "anothersecret", "salt")
        self.assertTrue(result)
        user_count = quarterapp.storage.get_user_count(self.db)
        self.assertEqual(2, user_count)

    def test_unique_username(self):
        result = quarterapp.storage.username_unique(self.db, "bob@example.com")
        self.assertTrue(result)

        result = quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        result = quarterapp.storage.username_unique(self.db, "bob@example.com")
        self.assertFalse(result)

    def test_user_salt(self):
        result = quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "mineral")
        self.assertEqual("mineral", quarterapp.storage.user_salt(self.db, "bob@example.com"))

    def test_delete_user(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "robert@example.com", "secretpassword", "salt")
        
        user_count = quarterapp.storage.get_user_count(self.db)
        self.assertEqual(3, user_count)

        quarterapp.storage.delete_user(self.db, "bobby@example.com")
        user_count = quarterapp.storage.get_user_count(self.db)
        self.assertEqual(2, user_count)

    def test_authenticate_user(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")

        result = quarterapp.storage.authenticate_user(self.db, "bobby@example.com", "secretpassword")
        self.assertIsNotNone(result)

    def test_authenticate_user_fail(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")

        result = quarterapp.storage.authenticate_user(self.db, "bobby@example.com", "iamahacker")
        self.assertIsNone(result)        

    def test_reset_user_password(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")

        result = quarterapp.storage.set_user_reset_code(self.db, "bobby@example.com", "okay")
        self.assertTrue(result)

        result = quarterapp.storage.reset_password(self.db, "no way", "anothersecret")
        self.assertFalse(result)

        result = quarterapp.storage.reset_password(self.db, "okay", "anothersecret")
        self.assertTrue(result)

    def test_reset_does_not_affect_password(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")

        result = quarterapp.storage.authenticate_user(self.db, "bobby@example.com", "secretpassword")
        self.assertIsNotNone(result)

        result = quarterapp.storage.set_user_reset_code(self.db, "bobby@example.com", "okay")
        self.assertTrue(result)

        result = quarterapp.storage.authenticate_user(self.db, "bobby@example.com", "secretpassword")
        self.assertIsNotNone(result)

    def test_user_is_enabled_by_default(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")

        result = quarterapp.storage.enabled_user(self.db, "bob@example.com")
        self.assertTrue(result)

    def test_disable_user(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")

        quarterapp.storage.disable_user(self.db, "bob@example.com")
        result = quarterapp.storage.enabled_user(self.db, "bob@example.com")
        self.assertFalse(result)

    def test_enable_user(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")

        quarterapp.storage.enable_user(self.db, "bob@example.com")
        result = quarterapp.storage.enabled_user(self.db, "bob@example.com")
        self.assertTrue(result)

    def test_filtered_user_count(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "robert@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "alice@internet.com", "secretpassword", "salt")

        result = quarterapp.storage.get_filtered_user_count(self.db, "example.com")
        self.assertEqual(3, result)

        result = quarterapp.storage.get_filtered_user_count(self.db, "alice")
        self.assertEqual(1, result)

        result = quarterapp.storage.get_filtered_user_count(self.db, "smhi.se")
        self.assertEqual(0, result)

    def test_get_users(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "robert@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "alice@internet.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "jane@internet.com", "secretpassword", "salt")

        result = quarterapp.storage.get_users(self.db, 0)
        self.assertEqual(5, len(result))

        result = quarterapp.storage.get_users(self.db, 0, 2)
        self.assertEqual(2, len(result))

        result = quarterapp.storage.get_users(self.db, 5)
        self.assertEqual(0, len(result))

    def test_get_users(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "robert@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "alice@internet.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "jane@internet.com", "secretpassword", "salt")

        result = quarterapp.storage.get_filtered_users(self.db, "example", 0)
        self.assertEqual(3, len(result))

        result = quarterapp.storage.get_filtered_users(self.db, "example", 5)
        self.assertEqual(0, len(result))

        result = quarterapp.storage.get_filtered_users(self.db, ".com", 1)
        self.assertEqual(4, len(result))

    def test_user_is_admin(self):
        quarterapp.storage.add_user(self.db, "admin@example.com", "secretpassword", "salt", quarterapp.storage.User.Administrator)
        quarterapp.storage.add_user(self.db, "notadmin@example.com", "secretpassword", "salt", quarterapp.storage.User.Normal)

        result = quarterapp.storage.is_admin(self.db, "admin@example.com")
        self.assertTrue(result)

        result = quarterapp.storage.is_admin(self.db, "notadmin@example.com")
        self.assertFalse(result)

    def test_change_password(self):
        quarterapp.storage.add_user(self.db, "bob@example.com", "secretpassword", "salt")
        quarterapp.storage.add_user(self.db, "bobby@example.com", "secretpassword", "salt")
        
        result = quarterapp.storage.authenticate_user(self.db, "bobby@example.com", "secretpassword")
        self.assertIsNotNone(result)

        quarterapp.storage.change_password(self.db, "bobby@example.com", "topsecretpassword")

        result = quarterapp.storage.authenticate_user(self.db, "bobby@example.com", "topsecretpassword")
        self.assertIsNotNone(result)
        
    ## Test settings

    def test_default_settings(self):
        settings = QuarterSettings(self.db)
        self.assertEqual("1", settings.get_value("allow-signups"))
        self.assertEqual("1", settings.get_value("allow-activations"))
    
    def test_all_settings(self):
        all_settings = quarterapp.storage.get_settings(self.db)
        self.assertEqual(2, len(all_settings))

    def test_update_setting(self):
        settings = QuarterSettings(self.db)
        self.assertEqual("1", settings.get_value("allow-signups"))

        settings.put_value("allow-signups", "0")
        self.assertEqual("0", settings.get_value("allow-signups"))

        # Restore
        settings.put_value("allow-signups", "1")

    def test_setting_cache(self):
        settings = QuarterSettings(self.db)
        self.assertEqual("1", settings.get_value("allow-signups"))

        # Update in database
        quarterapp.storage.put_setting(self.db, "allow-signups", "nwe")
        self.assertEqual("1", settings.get_value("allow-signups"))

        # Restore to not messup next test
        quarterapp.storage.put_setting(self.db, "allow-signups", "1")

    def test_setting_sync(self):
        settings = QuarterSettings(self.db)
        self.assertEqual("1", settings.get_value("allow-signups"))

        settings.put_value("allow-signups", "0")

        self.assertEqual("0", quarterapp.storage.get_setting(self.db, "allow-signups"))
        settings.put_value("allow-signups", "1")
        
    def test_settings_db(self):
        quarterapp.storage.put_setting(self.db, "allow-signups", "w")
        self.assertEqual("w", quarterapp.storage.get_setting(self.db, "allow-signups"))
        quarterapp.storage.put_setting(self.db, "allow-signups", "1")
