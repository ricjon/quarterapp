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
import math
import sys
import tornado.web

from quarterapp.storage import *

DEFAULT_PAGINATION_ITEMS_PER_PAGE = 5
DEFAULT_PAGINATION_PAGES = 10
SUCCESS = 0

class BaseHandler(tornado.web.RequestHandler):
    def write_success(self):
        self.write({
            "error" : SUCCESS,
            "message" :"Ok"})
        self.finish()

    def respond_with_error(self, error_code, error_message):
        logging.warning(error_message)
        self.write({
            "error" : error_code,
            "message" : error_message})
        self.finish()

    def write_unauthenticated_error(self):
        self.write({
            "error" : ERROR_NOT_AUTHENTICATED,
            "message" :"Not logged in"})
        self.finish()


class AuthenticatedHandler(BaseHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return tornado.escape.json_decode(user_json)


class ProtectedStaticHandler(tornado.web.StaticFileHandler):
    """
    Handle static files that are protected.
    """
    @tornado.web.authenticated
    def get(self, path, include_body=True):
        super(tornado.web.StaticFileHandler, self.get(path, include_body))


class SettingsHandler(BaseHandler):
    """Used as the HTTP API to retrieve and update application settings.
    User must be authenticated as administrator to be able to use
    """
    def get(self, key):
        try:
            if key:
                value = self.application.quarter_settings.get_value(key)
                if value:
                    self.write({"key" : key, "value" : value})
                    self.finish()
                else:
                    self.respond_with_error(101, "Could not retrieve setting (%s)".format(key))
            else:
                self.respond_with_error(102, "No key given")
        except:
            self.respond_with_error(100, "Could not retrieve setting (%s)".format(key))

    def post(self, key):
        try:
            if key:
                value = self.get_argument("value", "")
                self.application.quarter_settings.put_value(key, value)
                self.write({"key" : key, "value" : value})
                self.finish()
            else:
                self.respond_with_error(103, "No value specified for key (%s)".format(key))
        except:
            self.respond_with_error(104, "Could not update key (%s)".format(key))

class AdminDefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(u"admin/general.html")


class AdminUsersHandler(tornado.web.RequestHandler):
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

                self.render(u"admin/users.html", users = users, pagination = pagination_links, error = False, query_filter = query_filter)
            except:
                logging.error("Could not get users: %s", sys.exc_info())
                self.render(u"admin/users.html", users = [], pagination = [], error = True, query_filter = query_filter)
        else:
            self.render(u"admin/users.html", users = [], pagination = [], error = False, query_filter = query_filter)

    def post(self):
        self.get()

class AdminDisableUser(BaseHandler):
    def post(self, username):
        if len(username) > 0:
            try:
                disable_user(self.application.db, username)
                self.write_success()
            except:
                logging.error("Could not disble user: %s", sys.exc_info())
                self.respond_with_error(300, "Could not disble the given user")
        else:
            logging.error("Could not disble user - no user given: %s", sys.exc_info())
            self.respond_with_error(301, "Could not disble user - no user given")
        

class AdminEnableUser(BaseHandler):
    def post(self, username):
        if len(username) > 0:
            try:
                enable_user(self.application.db, username)
                self.write_success()
            except:
                logging.error("Could not enable user: %s", sys.exc_info())
                self.respond_with_error(302, "Could not enable the given user")
        else:
            logging.error("Could not enable user - no user given: %s", sys.exc_info())
            self.respond_with_error(303, "Could not enable user - no user given")


class AdminDeleteUser(BaseHandler):
    def post(self, username):
        if len(username) > 0:
            try:
                delete_user(self.application.db, username)
                self.write_success()
            except:
                logging.error("Could not delete user: %s", sys.exc_info())
                self.respond_with_error(304, "Could not delete the given user")
        else:
            logging.error("Could not delete user - no user given: %s", sys.exc_info())
            self.respond_with_error(305, "Could not delete user - no user given")


class AdminNewUserHandler(BaseHandler):
    def get(self):
        self.render(u"admin/new-user.html", completed = False, error = False)

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
                add_user(self.application.db, username, password, ut)
                self.render(u"admin/new-user.html", completed = True, error = False)
            except:
                self.render(u"admin/new-user.html", completed = False, error = True)
        else:
            self.render(u"admin/new-user.html", completed = False, error = True)

class AdminStatisticsHandler(tornado.web.RequestHandler):
    def get(self):
        user_count = get_user_count(self.application.db)
        signup_count = 0
        quarter_count = 0

        self.render(u"admin/statistics.html",
            user_count = user_count, signup_count = signup_count, quarter_count = signup_count)


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/")


class SignupHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(u"signup.html")


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(u"login.html")


class HeartbeatHandler(tornado.web.RequestHandler):
    """
    Heartbeat timer, just echo server health
    """
    def get(self):
        self.write("beat");
