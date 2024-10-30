import secrets
from flask import Flask

class App():
    def __init__(self, router):
        self.application = Flask(import_name=__name__)
        self.application.secret_key = secrets.token_hex(32)
        self.application.register_blueprint(router.bp)

        # main route
        ## ~~

    def run(self, _HOST, _PORT, _DEBUG=False):
        self.application.run(_HOST, _PORT, debug=_DEBUG)