from flask import Blueprint, flash, redirect, render_template, request, jsonify, session, url_for
import config
from modules.auth import login_required

bp = Blueprint('workspace', __name__, url_prefix='/workspace')

@bp.route('/make', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('workspace/make.html')