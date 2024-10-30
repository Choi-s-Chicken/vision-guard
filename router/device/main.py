from flask import Blueprint, flash, redirect, render_template, request, jsonify, session, url_for
import config
from modules.auth import login_required

bp = Blueprint('device', __name__, url_prefix='/device')

@bp.route('/regi', methods=['GET', 'POST'])
@login_required
def regi():
    if request.method == 'POST':
        print(request.form.keys())
        return {'result': 'success'}
    
    return render_template('device/regi.html', user_info=session.get('user_info'))