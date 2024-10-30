from flask import Blueprint, request, jsonify, render_template, send_from_directory, session
import router.user.main as user
import router.dashboard.main as dashboard
import router.workspace.main as workspace
import router.device.main as device

bp = Blueprint('main', __name__)
bp.register_blueprint(user.bp)
bp.register_blueprint(dashboard.bp)
bp.register_blueprint(workspace.bp)
bp.register_blueprint(device.bp)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.form.keys())
        return {'result': 'success'}
    return render_template('index.html', user_info=session.get('user_info'))

@bp.route('/process')
def process():
    request.form.get('')
    
@bp.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')