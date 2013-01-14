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

import smtplib
import logging
import sys

import tornado.template
from tornado.options import options

signup_email_template = tornado.template.Template("""From: Quarterapp <{{ email_from }}>
To: {{ email_to }}
Subject: {{ subject }}

Welcome to Quarterapp in order to complete your free registration you need to activate
your account.

Follow this link to complete the activation: {{ code_link }}

If the above link does not work, go to {{ link }} and enter the code manually.

Activation code: {{ code }}

Cheers!
 Quarterapp team

""")

reset_email_template = tornado.template.Template("""From: Quarterapp <{{ email_from }}>
To: {{ email_to }}
Subject: {{ subject }}

Someone - hopefully you - reported that you forgot your password to Quarterapp.

Follow this link to assign a new password to your account: {{ code_link }}

If the above link does not work, go to {{ link }} and enter the code manually.

Reset code: {{ code }}

If you did not ask to reset your password, please ignore this mail.

Cheers!
 Quarterapp team

""")

def send_mail(username, message):
    try:
        server = smtplib.SMTP(options.mail_host)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(options.mail_user, options.mail_password)
        server.sendmail(options.mail_sender, username, message)
        return True
    except:
        logging.warn("Could not send email: %s", sys.exc_info())
        return False

def send_signup_email(username, code):
    """
    Sends the activation email to the given address with the given activation code.

    @param username The username to send the email to
    @param code The activation code
    @return True if mail could be sent, else False
    """
    try:
        message = signup_email_template.generate(subject = "Welcome to quarterapp",
                    email_from = options.mail_sender,
                    email_to = username,
                    code_link = "http://" + options.base_url + "/activate/" + code,
                    link = "http://" + options.base_url + "/activate",
                    code = code)
        return send_mail(username, message)
    except:
        logging.warn("Could not send signup email: %s", sys.exc_info())
        return False

def send_reset_email(username, code):
    """
    Sends the password reset email to the given address with the given reset code.
    @param username The username to send the email to
    @param code The activation code
    @return True if mail could be sent, else False
    """
    try:
        message = reset_email_template.generate(subject = "Reset your password",
                    email_from = options.mail_sender,
                    email_to = username,
                    code_link = "http://" + options.base_url + "/reset/" + code,
                    link = "http://" + options.base_url + "/reset",
                    code = code)
        return send_mail(username, message)
    except:
        logging.warn("Could not send reset email: %s", sys.exc_info())
        return False
