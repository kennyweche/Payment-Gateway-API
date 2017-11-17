import requests
import sys

class Auth:
    username = None
    password = None
    app = None
    alg = None

    def __init__(self, app, alg, username, password):
        self.username = username
        self.password = password
        self.app = app
        self.alg = alg

    """
    Get auth status
    """
    def is_authenticated(self):
        return True
        self.alg.write_log(self.app, "authenticating user -> %s ####" % self.username, "info")
        try:
            post_data = {'username': self.username, 'password': self.password, 'clientId': self.app.config['auth_id']}
            self.alg.write_log(self.app, "authenticate data -> %s ####" % str(post_data), "info")
            post_response = requests.post(url=self.app.config['auth_url'], data=post_data)
            self.alg.write_log(self.app, "authenticate response %s " % str(post_response.status_code), "info")
            if post_response.status_code is not 200:
                return False
            return True
        except:
            error = str(sys.exc_info()[1])
            self.alg.write_log(self.app, "Error with authentication ->%s" % str(error), "error")
            return False
