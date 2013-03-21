#!/usr/bin/env python
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

import os
import logging
import sys
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.options
from tornado.options import options, define

from settings import QuarterSettings
from account import *
from admin import *
from api import *
from app import *
from quarter_utils import *

def read_configuration():
    """
    Setup expected options and parse from commandline and configuration file
    """
    define("base_url", help="Application base URL (including port but not schema")
    define("port", type=int, help="Port to listen on")
    define("app_config_age", type=int, help="Time in minutes between application config update")
    define("cookie_secret", help="Random long hexvalue to secure cookies")
    define("mysql_host", help="MySQL hostname")
    define("mysql_port", help="MySQL port", type=int)
    define("mysql_database", help="MySQL database name")
    define("mysql_user", help="MySQL username")
    define("mysql_password", help="MySQL password")
    define("backend", help="Choice of backend, sqlite or mysql")
    define("sqlite_database", help="SQLite3 database file")
    define("mail_host", help="SMTP host name")
    define("mail_port", type=int, help="SMTP port number")
    define("mail_user", help="SMTP Authentication username")
    define("mail_password", help="SMTP Authentication password")
    define("mail_sender", help="Email sender address")
    define("google_analytics", help="Google Analytics account to use")
    define("compressed_resources", type=bool, help="Use compress JavaScript and CSS")

    try:
        tornado.options.parse_command_line()
        tornado.options.parse_config_file("quarterapp.conf")
        
    except IOError:
        logging.warning("Configuration file not found (quarterapp.conf)!")
        exit(1)

def quarterapp_main():
    application = tornado.web.Application(
        # Application routes
        [
            # Administration
            (r"/admin", AdminDefaultHandler),
            (r"/admin/users", AdminUsersHandler),
            (r"/admin/new-user", AdminNewUserHandler),
            (r"/admin/statistics", AdminStatisticsHandler),
            (r"/admin/enable/([^\/]+)", AdminEnableUser),
            (r"/admin/disable/([^\/]+)", AdminDisableUser),
            (r"/admin/delete/([^\/]+)", AdminDeleteUser),
            (r"/admin/settings/([^\/]+)", SettingsHandler),

            # Authentication handlers
            (r"/logout", LogoutHandler),
            (r"/signup", SignupHandler),
            (r"/activate", ActivationHandler),
            (r"/activate/([^\/]+)", ActivationHandler),
            (r"/forgot", ForgotPasswordHandler),
            (r"/reset/([^\/]+)", ResetPasswordHandler),
            (r"/reset", ResetPasswordHandler),
            (r"/login", LoginHandler),
            (r"/terms", TermsHandler),
            (r"/password", ChangePasswordHandler),
            (r"/delete-account", DeleteAccountHandler),

            # Application views
            (r"/activities", ActivityHandler),
            (r"/sheet", SheetHandler),
            (r"/sheet/([^\/]+)", SheetHandler),
            (r"/profile", ProfileHandler),
            (r"/report", ReportHandler),

            # Application API
            (r"/api/activities", ActivityApiHandler),
            (r"/api/activity", ActivityApiHandler),
            (r"/api/activity/([^\/]+)", ActivityApiHandler),
            (r"/api/sheet/([^\/]+)", SheetApiHandler),
            (r"/", IndexHandler),
            
            (r".*", Http404Handler)
        ],

        # Static files
        static_path = os.path.join(os.path.dirname(__file__), "resources/static"),
        
        # Location of HTML templates
        template_path = os.path.join(os.path.dirname(__file__), "resources/templates"),

        # Enable HTTP compression
        gzip = True,

        # Application specific cookie hash
        cookie_secret = options.cookie_secret,

        login_url = "/login"
    )

    logging.info("Starting application...")
    main_loop = tornado.ioloop.IOLoop.instance()

    application.db = DbConnection()

    # Setup application settings
    application.quarter_settings = QuarterSettings(application.db)

    # Setup periodic callback to update application settings
    config_loop = tornado.ioloop.PeriodicCallback(application.quarter_settings.update,
        options.app_config_age * 60 * 1000, io_loop = main_loop)

    config_loop.start()
    
    try:
        application.listen(options.port)
        main_loop.start()
    except KeyboardInterrupt:
        logging.info("Quitting application")
    except:
        logging.error("Could not start application: %s", sys.exc_info()[0])
        print("Could not start application!")
        exit()

def main():
    """Entry point"""

    if 'mkconfig' in sys.argv:
        import settings
        settings.create_default_config('.')
        return
    read_configuration()
    quarterapp_main()


if __name__ == "__main__":
    main()