from flask import Blueprint, request, jsonify, render_template
import router.user.main as user

bp = Blueprint('main', __name__)
bp.register_blueprint(user.bp)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/process')
def process():
    request.form.get('')