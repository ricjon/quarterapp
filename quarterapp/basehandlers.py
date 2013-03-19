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
import functools

import tornado.web
from tornado import escape
from tornado.options import options
from tornado.escape import utf8

from storage import *
from quarter_errors import *
from settings import *
from domain import *

class QuarterEncoder(json.JSONEncoder):
    """
    JSON encoder for error objects
    """
    def default(self, obj):
        if isinstance(obj, ApiError):
            return { "code" : obj.code, "message" : obj.message }
        elif isinstance(obj, Activity):
            return { 'id' : obj.id, 'title' : obj.title, 'color' : obj.color.hex() }

def authenticated_user(method):
    """
    Decorate methods with this to require that the user be logged in.
    """
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
    """
    Decorate methods with this to require that user is admin, if not, render 404 (to avoid exposing admin part)
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise tornado.web.HTTPError(404)
        elif not is_admin(self.application.db, self.current_user["username"]):
            raise tornado.web.HTTPError(404)
        return method(self, *args, **kwargs)
    return wrapper

class BaseHandler(tornado.web.RequestHandler):
    """
    Base handler for any handler in quarterapp, contains some utility functions
    """
    def json(self, chunk):
        chunk = QuarterEncoder().encode(chunk).replace("'", "\"")
        chunk = utf8(chunk)
        self._write_buffer.append(chunk)
        self.set_header("Content-Type", "application/json; charset=UTF-8")

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

    def logged_in(self):
        """
        Check if the user of the current requests is logged in or not.

        @return True if logged in, else False
        """
        user = self.get_secure_cookie("user")
        if user:
            return True
        else:
            return False

    def setting_value(self, key):
        """
        Get the given value from the quarter settings

        @return The value for the given setting key
        """
        return self.application.quarter_settings.get_value(key)

class AuthenticatedHandler(BaseHandler):
    """
    Base class for any handler that needs user to be authenticated
    """
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

    def get_current_user_id(self):
        user = self.get_current_user()
        if user:
            return user["id"]
        return None

class IndexHandler(BaseHandler):
    def get(self):
        self.render(u"public/index.html",
            options = options,
            allow_signups = self.setting_value("allow-signups"),
            logged_in = self.logged_in())

class TermsHandler(BaseHandler):
    def get(self):
        self.render(u"public/terms.html",
            options = options,
            logged_in = self.logged_in())

class Http404Handler(BaseHandler):
    def get(self):
        self.render(u"public/404.html",
            options = options,
            logged_in = self.logged_in())