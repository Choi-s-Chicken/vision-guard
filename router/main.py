from flask import Blueprint, request, jsonify, render_template, send_from_directory, session
import router.user.main as user
import router.dashboard.main as dashboard
import router.workspace.main as workspace
import router.device.main as device

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html', user_info=session.get('user_info'))

@bp.route('/asus', methods=['GET'])
def index_asus():
    return render_template('index_asus.html', user_info=session.get('user_info'))

@bp.route('/process')
def process():
    request.form.get('')
    
@bp.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

bp.register_blueprint(user.bp)
bp.register_blueprint(dashboard.bp)
bp.register_blueprint(workspace.bp)
bp.register_blueprint(device.bp)