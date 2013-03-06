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
import sys
import os

import tornado.web
import tornado.escape
from tornado.options import options

from basehandlers import *
from storage import *
from email_utils import *
from quarter_errors import *
from quarter_utils import *

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/")

class SignupHandler(BaseHandler):
    def get(self):
        if self.enabled("allow-signups"):
            self.render(u"public/signup.html", options = options, error = None, username = "")
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
                code = activation_code()
                if send_signup_email(username, code):
                    signup_user(self.application.db, username, code, self.request.remote_ip)
                    self.render(u"public/signup_instructions.html", options = options)
                else:
                    self.render(u"public/signup.html", options = options, error = error, username = username)    
            except Exception, e:
                logging.error("Could not signup user: %s" % (e,))
                self.render(u"public/signup.html", options = options, error = error, username = username)
        else:
            self.render(u"public/signup.html", options = options, error = error, username = username)


class ActivationHandler(BaseHandler):
    def get(self, code_parameter = None):
        code = None
        if code_parameter:
            code = code_parameter
        
        if self.enabled("allow-activations"):
            self.render(u"public/activate.html", options = options, error = None, code = code)
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
            self.render(u"public/activate.html", options = options, error = "not_valid", code = None)
        else:
            salt = username_for_activation_code(self.application.db, code)
            salted_password = hash_password(password, salt)
            if activate_user(self.application.db, code, salted_password, salt):
                # TODO Do login
                self.redirect(u"/sheet")
            else:
                self.render(u"public/activate.html", options = options, error = "unknown", code = code)

class ForgotPasswordHandler(BaseHandler):
    def get(self):
        self.render(u"public/forgot.html", options = options, error = None, username = None)

    def post(self):
        username = self.get_argument("username", "")
        error = False
        if len(username) == 0:
            self.render(u"public/forgot.html", options = options, error = "empty", username = username)
        else:
            reset_code = activation_code()
            if set_user_reset_code(self.application.db, username, reset_code):
                send_reset_email(username, reset_code)
                self.redirect(u"/reset")
            else:
                self.render(u"public/forgot.html", options = options, error = "unknown", username = username)

class ResetPasswordHandler(BaseHandler):
    def get(self, code_parameter = None):
        code = None
        if code_parameter:
            code = code_parameter
        self.render(u"public/reset.html", options = options, error = None, code = code)

    def post(self):
        code = self.get_argument("code", "")
        password = self.get_argument("password", "")
        verify_password = self.get_argument("verify-password", "")

        error = None
        if len(code) == 0:
            error = "not_valid"
        if len(password) == 0:
            error = "not_valid"
        if not password == verify_password:
            error = "not_matching"

        if error:
            self.render(u"public/reset.html", options = options, error = "unknown", code = code)
        else:
            salt = username_for_activation_code(self.application.db, code)
            salted_password = hash_password(password, salt)
            if reset_password(self.application.db, code, salted_password):
                # TODO Do login
                self.redirect(u"/sheet")
            else:
                self.render(u"public/reset.html", options = options, error = "unknown", code = code)

class LoginHandler(AuthenticatedHandler):
    def get(self):
        allow_signups = self.application.quarter_settings.get_value("allow-signups")

        self.render(u"public/login.html", options = options, error = None, allow_signups = allow_signups)

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        hashed_password = hash_password(password, username)

        user = authenticate_user(self.application.db, username, hashed_password)
        if user:
            logging.warn("User authenticated")
            self.set_current_user(user)
            self.redirect(u"/sheet")
        else:
            logging.warn("User not authenticated")
            self.set_current_user(None)

            allow_signups = self.application.quarter_settings.get_value("allow-signups")
            self.render(u"public/login.html", options = options, error = "unauthenticated", allow_signups = allow_signups)

class ChangePasswordHandler(AuthenticatedHandler):
    @authenticated_user
    def get(self):
        self.render(u"app/password.html", options = options, error = None)

    @authenticated_user
    def post(self):
        current_password = self.get_argument("current-password", "")
        new_password = self.get_argument("new-password", "")
        verify_password = self.get_argument("verify-password", "")
        username = self.current_user["username"]

        error = None
        if len(current_password) == 0:
            error = "not_valid"
        if len(new_password) == 0:
            error = "not_valid"
        if not new_password == verify_password:
            error = "not_matching"

        current_hash = hash_password(current_password, username)
        authenticated = authenticate_user(self.application.db, username, current_hash)

        if not authenticated:
            error = "not_valid"

        if error:
            self.render(u"app/password.html", options = options, error = error)
        else:
            hashed_password = hash_password(new_password, username)
            change_password(self.application.db, username, hashed_password)
            self.render(u"app/password.html", options = options, error = "success")
