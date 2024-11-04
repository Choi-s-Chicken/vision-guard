from flask import Blueprint, flash, redirect, render_template, request, jsonify, session, url_for
import config
import modules.device as device_ctrl
from modules.auth import login_required
import modules.space as space_ctrl

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', user_info=session.get('user_info'),
                           prcts=device_ctrl.get_device_db(), spaces=space_ctrl.get_db())

