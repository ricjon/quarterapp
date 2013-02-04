#
#  Copyright (c) 2013 Markus Eliasson, http://www.quarterapp.com/
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
import sys
import os

import tornado.web
import tornado.escape
from tornado.options import options

from quarterapp.basehandlers import *
from quarterapp.storage import *
from quarterapp.email import *
from quarterapp.errors import *
from quarterapp.utils import *

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
            salted_password = hash_password(password, options.salt)
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
            salted_password = hash_password(password, options.salt)
            if reset_password(self.application.db, code, salted_password):
                # TODO Do login
                self.redirect(u"/sheet")
            else:
                self.render(u"public/reset.html", error = "unknown", code = code)

class LoginHandler(AuthenticatedHandler):
    def get(self):
        self.render(u"public/login.html")

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        hashed_password = hash_password(password, options.salt)

        user = authenticate_user(self.application.db, username, hashed_password)
        if user:
            logging.warn("User authenticated")
            self.set_current_user(user)
            self.redirect(u"/sheet")
        else:
            logging.warn("User not authenticated")
            self.set_current_user(None)
            self.render(u"public/login.html")
