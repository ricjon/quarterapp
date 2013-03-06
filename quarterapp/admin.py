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
import math
import sys
import os
import json

import tornado.web
import tornado.escape
from tornado.options import options
from tornado.web import HTTPError

from basehandlers import *
from storage import *
from quarter_errors import *
from quarter_utils import *

DEFAULT_PAGINATION_ITEMS_PER_PAGE = 5
DEFAULT_PAGINATION_PAGES = 10

class AdminDefaultHandler(AuthenticatedHandler):
    """
    Renders the admin first view
    """
    @authenticated_admin
    def get(self):
        allow_signups = self.application.quarter_settings.get_value("allow-signups")
        allow_activations = self.application.quarter_settings.get_value("allow-activations")

        self.render(u"admin/general.html",
            options = options, allow_signups = allow_signups, allow_activations = allow_activations)

class AdminUsersHandler(AuthenticatedHandler):
    """
    Handler for user listing and searching
    """
    @authenticated_admin
    def generate_pagination(self, total, current, max_per_page, max_links, query_filter = None):
        """
        Generate a list of pagination links based on the following input.

        Try to keep the current page at the center of the returned list

        @param total The total number of items (not per page)
        @param current The current position / index within that range (0:total)
        @param max_per_page The maximum number of links per page
        @param max_pages The maximum number of pagination links to return
        """
        pagination = []
        total_pages = 0
        current_page = 0
        
        try:
            if total == 0:
                total_pages = 0
            elif int(total) < int(max_per_page):
                total_pages = 1
            else:
                total_pages = int(total) / int(max_per_page)
                if int(total) % int(max_per_page) != 0:
                    total_pages = total_pages + 1 
            
            if int(current) < int(max_per_page):
                current_page = 0
            else:
                current_page = int(current) / int(max_per_page)

            for i in range(total_pages):
                start = int(i) * int(max_per_page)

                link = ""
                if query_filter:
                    link = "/admin/users?start={0}&count={1}&filter={2}".format(start, max_per_page, query_filter)
                else:
                    link = "/admin/users?start={0}&count={1}".format(start, max_per_page)

                current_page = int(start) <= int(current) < (int(start) + int(max_per_page))
                
                p = { 'index' : i, 'link' : link, 'current' : current_page }
                pagination.append(p)

        except:
            logging.warn("Could not generate the users pagination: %s", sys.exc_info())

        return pagination

    @authenticated_admin
    def get(self):
        start = self.get_argument("start", "")
        count = self.get_argument("count", "")
        query_filter = self.get_argument("filter", "")
        
        users = []
        pagination_link = []
        error = False

        if len(start) > 0:
            if not start.isdigit():
                error = True
        else:
            start = 0 # Default start index

        if len(count) > 0:
            if not count.isdigit():
                error = True
        else:
            count = DEFAULT_PAGINATION_ITEMS_PER_PAGE

        if not error:
            try:
                if query_filter:
                    user_count = get_filtered_user_count(self.application.db, query_filter)
                    pagination_links = self.generate_pagination(user_count, start, count, DEFAULT_PAGINATION_PAGES, query_filter = query_filter)
                    users = get_filtered_users(self.application.db, query_filter, start, count)
                else:
                    user_count = get_user_count(self.application.db)
                    pagination_links = self.generate_pagination(user_count, start, count, DEFAULT_PAGINATION_PAGES)
                    users = get_users(self.application.db, start, count)

                self.render(u"admin/users.html", options = options, users = users, pagination = pagination_links, error = False, query_filter = query_filter)
            except:
                logging.error("Could not get users: %s", sys.exc_info())
                self.render(u"admin/users.html", options = options, users = [], pagination = [], error = True, query_filter = query_filter)
        else:
            self.render(u"admin/users.html", options = options, users = [], pagination = [], error = False, query_filter = query_filter)

    @authenticated_admin
    def post(self):
        self.get()

class AdminNewUserHandler(AuthenticatedHandler):
    """
    Handler for creating new users as administrator
    """
    @authenticated_admin
    def get(self):
        self.render(u"admin/new-user.html", options = options, completed = False, error = False)

    @authenticated_admin
    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        verify_password = self.get_argument("verify-password", "")
        user_type = self.get_argument("user-type", "")
        
        ut = User.Normal
        if user_type == "admin":
            ut = User.Administrator
            
        error = False
        if len(username) == 0:
            error = True
        if not password == verify_password:
            error = True
        if not username_unique(self.application.db, username):
            error = True

        if not error:
            try:
                salt = username
                salted_password = hash_password(password, salt)
                add_user(self.application.db, username, salted_password, salt, ut)
                self.render(u"admin/new-user.html", options = options, completed = True, error = False)
            except:
                self.render(u"admin/new-user.html", options = options, completed = False, error = True)
        else:
            self.render(u"admin/new-user.html", options = options, completed = False, error = True)

class AdminStatisticsHandler(AuthenticatedHandler):
    """
    Handler for rendering the statistics view
    """
    @authenticated_admin
    def get(self):
        user_count = get_user_count(self.application.db)
        signup_count = get_signup_count(self.application.db)
        quarter_count = 0

        self.render(u"admin/statistics.html",
            options = options, user_count = user_count, signup_count = signup_count, quarter_count = quarter_count)

#
# Admin API handlers
#

class SettingsHandler(AuthenticatedHandler):
    """
    Used as the HTTP API to retrieve and update application settings.
    User must be authenticated as administrator to be able to use
    """
    @authenticated_admin
    def get(self, key):
        try:
            if key:
                value = self.application.quarter_settings.get_value(key)
                if value:
                    self.write({"key" : key, "value" : value})
                    self.finish()
                else:
                    self.respond_with_error(ERROR_RETRIEVE_SETTING)
            else:
                self.respond_with_error(ERROR_NO_SETTING_KEY)
        except:
            self.respond_with_error(ERROR_RETRIEVE_SETTING)

    @authenticated_admin
    def post(self, key):
        try:
            if key:
                value = self.get_argument("value", "")
                self.application.quarter_settings.put_value(key, value)
                self.write({"key" : key, "value" : value})
                self.finish()
            else:
                self.respond_with_error(ERROR_NO_SETTING_VALUE)
        except Exception, e:
            logging.warn("Could not update setting %s" % e)
            self.respond_with_error(ERROR_UPDATE_SETTING)

class AdminDisableUser(AuthenticatedHandler):
    @authenticated_admin
    def post(self, username):
        if len(username) > 0:
            try:
                disable_user(self.application.db, username)
                self.write_success()
            except:
                logging.error("Could not disble user: %s", sys.exc_info())
                self.respond_with_error(ERROR_DISABLE_USER)
        else:
            logging.error("Could not disble user - no user given: %s", sys.exc_info())
            self.respond_with_error(ERROR_DISABLE_NO_USER)
        
class AdminEnableUser(AuthenticatedHandler):
    @authenticated_admin
    def post(self, username):
        if len(username) > 0:
            try:
                enable_user(self.application.db, username)
                self.write_success()
            except:
                logging.error("Could not enable user: %s", sys.exc_info())
                self.respond_with_error(ERROR_ENABLE_USER)
        else:
            logging.error("Could not enable user - no user given: %s", sys.exc_info())
            self.respond_with_error(ERROR_ENABLE_NO_USER)

class AdminDeleteUser(AuthenticatedHandler):
    @authenticated_admin
    def post(self, username):
        if len(username) > 0:
            try:
                delete_user(self.application.db, username)
                self.write_success()
            except:
                logging.error("Could not delete user: %s", sys.exc_info())
                self.respond_with_error(ERROR_DELETE_USER)
        else:
            logging.error("Could not delete user - no user given: %s", sys.exc_info())
            self.respond_with_error(ERROR_DELETE_NO_USER)



