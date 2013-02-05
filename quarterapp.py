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

import os
import logging
import sys
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.options
import MySQLdb
from tornado.options import options, define

from quarterapp.settings import QuarterSettings
from quarterapp.account import *
from quarterapp.admin import *
from quarterapp.api import *
from quarterapp.app import *

def read_configuration():
    """
    Setup expected options and parse from commandline and configuration file
    """
    define("base_url", help="Application base URL (including port but not schema")
    define("port", type=int, help="Port to listen on")
    define("app_config_age", type=int, help="Time in minutes between application config update")
    define("cookie_secret", help="Random long hexvalue to secure cookies")
    define("salt", help="Password salt used")
    define("mysql_host", help="MySQL hostname")
    define("mysql_database", help="MySQL database name")
    define("mysql_user", help="MySQL username")
    define("mysql_password", help="MySQL password")
    define("mail_host", help="SMTP host name")
    define("mail_port", type=int, help="SMTP port number")
    define("mail_user", help="SMTP Authentication username")
    define("mail_password", help="SMTP Authentication password")
    define("mail_sender", help="Email sender address")

    try:
        tornado.options.parse_command_line()
        tornado.options.parse_config_file("quarterapp.conf")
    except IOError:
        logging.warning("Configuration file not found (quarterapp.conf)!")

def main():
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

            # Application views
            (r"/activities", ActivityHandler),
            (r"/sheet", SheetHandler),
            (r"/sheet/([^\/]+)", SheetHandler),

            # Application API
            (r"/api/activities", ActivityApiHandler),
            (r"/api/activity", ActivityApiHandler),
            (r"/api/activity/([^\/]+)", ActivityApiHandler),
            (r"/api/sheet/([^\/]+)", SheetApiHandler),
            (r"/", IndexHandler),
            
            # Static files
            (r"/(.*)", tornado.web.StaticFileHandler, { "path" : "static"})
        ],

        # Static files
        static_path = os.path.join(os.path.dirname(__file__), "static"),
        
        # Location of HTML templates
        template_path = os.path.join(os.path.dirname(__file__), "templates"),

        # Enable HTTP compression
        gzip = True,

        # Application specific cookie hash
        cookie_secret = options.cookie_secret,

        login_url = "/login"
    )

    logging.info("Starting application...")

    main_loop = tornado.ioloop.IOLoop.instance()

    # Setup database connection
    application.db = MySQLdb.connect(host=options.mysql_host, db=options.mysql_database,
        user=options.mysql_user, passwd=options.mysql_password)

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

if __name__ == "__main__":
        read_configuration()
        main()
