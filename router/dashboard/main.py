from flask import Blueprint, flash, redirect, render_template, request, jsonify, session, url_for
import config
from modules.auth import login_required

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', user_info=session.get('user_info'),
                           prcts=config.get_products_db())

