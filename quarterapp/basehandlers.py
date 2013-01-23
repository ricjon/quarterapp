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
import json
import functools

import tornado.web
import tornado.escape
from tornado.options import options

from quarterapp.storage import *
from quarterapp.email import *
from quarterapp.errors import *
from quarterapp.utils import *

class QuarterEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ApiError):
            return { "code" : obj.code, "message" : obj.message }

def authenticated_user(method):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                self.redirect(url)
                return
            raise tornado.web.HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper

def authenticated_admin(method):
    """Check if user is admin, if not, render 404 (to avoid exposing admin part) """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise tornado.web.HTTPError(404)
        elif self.current_user["type"] != User.Administrator:
            raise tornado.web.HTTPError(404)
        return method(self, *args, **kwargs)
    return wrapper

class BaseHandler(tornado.web.RequestHandler):    
    def write_success(self):
        """
        Respond with a successful code and HTTP 200
        """
        self.write({
            "error" : SUCCESS_CODE,
            "message" :"Ok"})
        self.finish()

    def respond_with_error(self, error):
        """
        Respond with a single error and HTTP 500
        """
        self.write({
            "error" : error.code,
            "message" : error.message })
        self.set_status(500)
        self.finish()

    def respond_with_errors(self, errors):
        """
        Respond with multiple errors (of type ApiError) and HTTP 500
        """
        self.write({
            "errors" : QuarterEncoder().encode(errors).replace("\"", "'") })
        self.set_status(500)
        self.finish()

    def write_unauthenticated_error(self):
        """
        Response with a HTTP 407 Unauthenticated
        """
        self.write({
            "error" : ERROR_NOT_AUTHENTICATED.code,
            "message" : ERROR_NOT_AUTHENTICATED.message })
        self.set_status(407)
        self.finish()

    def enabled(self, setting):
        """
        Check if the given setting is enabled

        @param setting The setting to check
        @return True if setting is enabled, else False
        """
        return self.application.quarter_settings.get_value(setting) == "1"

class AuthenticatedHandler(BaseHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return tornado.escape.json_decode(user_json)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")
