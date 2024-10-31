import re
from flask import Blueprint, flash, redirect, render_template, request, jsonify, session, url_for
import config
from modules.auth import login_required
import modules.space as space

bp = Blueprint('space', __name__, url_prefix='/space')

@bp.route('/make', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == "POST":
        space_name = request.form.get('space-name')
        find_allow_human = request.form.get('find-allow-human-work')
        find_notallow_human = request.form.get('find-notallow-human-work')
        find_unknown_human = request.form.get('find-unknown-human-work')
        
        
        if not space_name:
            flash('공간 이름을 입력하세요.', 'error')
            return redirect(url_for('main.space.index'))
        
        if re.match(config.SPACE_NM_RE, space_name) is None:
            flash('공간 이름은 한글, 영문, 숫자만 사용하여 2~16자 사이여야 합니다.', 'error')
            return redirect(url_for('main.space.index'))
        
        if not find_allow_human and not find_notallow_human and not find_unknown_human:
            flash('작업 옵션을 선택하세요.', 'error')
            return redirect(url_for('main.space.index'))
        
        work_list = ['0', '1', '2', '3']
        if find_allow_human not in work_list or find_notallow_human not in work_list or find_unknown_human not in work_list:
            flash('작업 옵션이 올바르지 않습니다.', 'error')
            return redirect(url_for('main.space.index'))
        
        
        space.add_space_db(space_name, find_allow_human, find_notallow_human, find_unknown_human)
        flash('공간이 생성되었습니다.', 'success')
        return redirect(url_for('main.dashboard.index'))
    
    return render_template('space/make.html')