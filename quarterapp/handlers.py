#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
#  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import tornado.web

class AuthenticatedHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return tornado.escape.json_decode(user_json)

    def write_success(self):
        self.write({
            "error" : SUCCESS,
            "message" :"Ok"})

    def write_general_error(self):
        self.write({
            "error" : ERROR_GENERAL_ERROR,
            "message" :"General error"})

    def write_unauthenticated_error(self):
        self.write({
            "error" : ERROR_NOT_AUTHENTICATED,
            "message" :"Not logged in"})

class ProtectedStaticHandler(tornado.web.StaticFileHandler):
    """
    Handle static files that are protected.
    """
    @tornado.web.authenticated
    def get(self, path, include_body=True):
        super(tornado.web.StaticFileHandler, self.get(path, include_body))

class AdminDefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(u"admin/general.html")

class AdminUsersHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(u"admin/users.html")

class AdminNewUserHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(u"admin/new-user.html")

class AdminStatisticsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(u"admin/statistics.html")

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