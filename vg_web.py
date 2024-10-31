import secrets
from flask import Flask, render_template

class App():
    def __init__(self, router):
        self.application = Flask(import_name=__name__)
        self.application.secret_key = secrets.token_hex(32)
        self.application.register_blueprint(router.bp)
        
        # error handlers
        @self.application.errorhandler(404)
        def error_404(e):
            return render_template('error/404.html'), 404

        @self.application.errorhandler(405)
        def error_405(e):
            return render_template('error/405.html'), 405

    def run(self, _HOST, _PORT, _DEBUG=False):
        self.application.run(_HOST, _PORT, debug=_DEBUG)