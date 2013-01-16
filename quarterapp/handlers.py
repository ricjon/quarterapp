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

import logging
import math
import sys
import os
import hashlib
import base64
import tornado.web

from tornado.options import options
from quarterapp.storage import *
from quarterapp.email import *

DEFAULT_PAGINATION_ITEMS_PER_PAGE = 5
DEFAULT_PAGINATION_PAGES = 10
SUCCESS = 0

sha = hashlib.sha512()

def hash_password(password):
    sha.update(password + options.salt)
    hashed_password = base64.urlsafe_b64encode(sha.digest())
    return hashed_password
    

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
        self.set_status(500)
        self.finish()

    def write_unauthenticated_error(self):
        self.write({
            "error" : ERROR_NOT_AUTHENTICATED,
            "message" :"Not logged in"})
        self.set_status(407)
        self.finish()

    def enabled(self, setting):
        """
        Check if the given setting is enabled
        """
        return self.application.quarter_settings.get_value(setting) == "1"


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
        allow_signups = self.application.quarter_settings.get_value("allow-signups")
        allow_activations = self.application.quarter_settings.get_value("allow-activations")

        self.render(u"admin/general.html",
            allow_signups = allow_signups, allow_activations = allow_activations)


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
                salted_password = hash_password(password)
                print "2"
                add_user(self.application.db, username, salted_password, ut)
                print "2"
                self.render(u"admin/new-user.html", completed = True, error = False)
            except:
                self.render(u"admin/new-user.html", completed = False, error = True)
        else:
            self.render(u"admin/new-user.html", completed = False, error = True)


class AdminStatisticsHandler(BaseHandler):
    def get(self):
        user_count = get_user_count(self.application.db)
        signup_count = get_signup_count(self.application.db)
        quarter_count = 0

        self.render(u"admin/statistics.html",
            user_count = user_count, signup_count = signup_count, quarter_count = quarter_count)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/")


class SignupHandler(BaseHandler):
    def get(self):
        if self.enabled("allow-signups"):
            self.render(u"public/signup.html", error = None, username = "")
        else:
            raise tornado.web.HTTPError(404)

    def post(self):
        if not self.enabled("allow-signups"):
            raise tornado.web.HTTPError(500)

        username = self.get_argument("email", "")

        error = False
        if len(username) == 0:
            error = "empty"
        if not username_unique(self.application.db, username):
            error = "not_unique"

        if not error:
            try:
                code = os.urandom(16).encode("base64")[:20]
                if send_signup_email(username, code):
                    signup_user(self.application.db, username, code, self.request.remote_ip)
                    self.render(u"public/signup_instructions.html")
                else:
                    logging.error("Could not signup user: %s", sys.exc_info())
                    self.render(u"public/signup.html", error = error, username = username)    
            except:
                logging.error("Could not signup user: %s", sys.exc_info())
                self.render(u"public/signup.html", error = error, username = username)
        else:
            self.render(u"public/signup.html", error = error, username = username)


class ActivationHandler(BaseHandler):
    def get(self, code_parameter = None):
        code = None
        if code_parameter:
            code = code_parameter
        
        if self.enabled("allow-activations"):
            self.render(u"public/activate.html", error = None, code = code)
        else:
            raise tornado.web.HTTPError(404)

    def post(self):
        if not self.enabled("allow-activations"):
            raise tornado.web.HTTPError(500)

        code = self.get_argument("code", "")
        password = self.get_argument("password", "")
        verify_password = self.get_argument("verify-password", "")

        error = None
        if len(code) == 0:
            error = "not_valid"
        if not password == verify_password:
            error = "not_matching"

        if error:
            self.render(u"public/activate.html", error = "not_valid", code = None)
        else:
            salted_password = hash_password(password)
            if activate_user(self.application.db, code, salted_password):
                # TODO Do login
                self.redirect(u"/sheet")
            else:
                self.render(u"public/activate.html", error = "unknown", code = code)

class ForgotPasswordHandler(BaseHandler):
    def get(self):
        self.render(u"public/forgot.html", error = None, username = None)

    def post(self):
        username = self.get_argument("username", "")
        error = False
        if len(username) == 0:
            self.render(u"public/forgot.html", error = "empty", username = username)
        else:
            reset_code = os.urandom(16).encode("base64")[:20]
            if set_user_reset_code(self.application.db, username, reset_code):
                send_reset_email(username, reset_code)
                self.redirect(u"/reset")
            else:
                self.render(u"public/forgot.html", error = "unknown", username = username)

class ResetPasswordHandler(BaseHandler):
    def get(self, code_parameter = None):
        code = None
        if code_parameter:
            code = code_parameter
        self.render(u"public/reset.html", error = None, code = code)

    def post(self):
        code = self.get_argument("code", "")
        password = self.get_argument("password", "")
        verify_password = self.get_argument("verify-password", "")

        error = None
        if len(code) == 0:
            error = "not_valid"
        if not password == verify_password:
            error = "not_matching"

        if error:
            self.render(u"public/reset.html", error = "unknown", code = code)
        else:
            salted_password = hash_password(password)
            if reset_password(self.application.db, code, salted_password):
                # TODO Do login
                self.redirect(u"/sheet")
            else:
                self.render(u"public/reset.html", error = "unknown", code = code)

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(u"public/login.html")

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(u"public/index.html")
        
class ActivityHandler(BaseHandler):
    def get(self):
        self.render(u"app/activities.html")

class SheetHandler(BaseHandler):
    def get(self):
        self.render(u"app/sheet.html")


