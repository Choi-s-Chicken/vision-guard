import re
from flask import Blueprint, flash, redirect, render_template, request, jsonify, session, url_for
import config
from modules.auth import login_required
import modules.space as space_ctrl
import modules.device as device_ctrl
import modules.user as user_ctrl

bp = Blueprint('space', __name__, url_prefix='/space')

@bp.route('/view/<space_uuid>')
@login_required
def view(space_uuid):
    space_db = space_ctrl.get_db()
    for space in space_db:
        if space['uuid'] == space_uuid:
            return render_template('space/view.html', space=space, users=user_ctrl.get_user_db(), regi_prcts=device_ctrl.get_device_db())
        
    flash('존재하지 않는 공간입니다.', 'error')
    return redirect(url_for('main.dashboard.index'))

@bp.route('/make', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == "POST":
        space_name = request.form.get('space-name')
        space_desc = request.form.get('space-desc')
        find_allow_human = request.form.get('find-allow-human-work')
        find_notallow_human = request.form.get('find-notallow-human-work')
        find_unknown_human = request.form.get('find-unknown-human-work')
        
        if not space_name:
            flash('공간 이름을 입력하세요.', 'error')
            return redirect(url_for('main.space.index'))
        
        if re.match(config.SPACE_NM_RE, space_name) is None:
            flash('공간 이름은 한글, 영문, 숫자만 사용하여 2~16자 사이여야 합니다.', 'error')
            return redirect(url_for('main.space.index'))
        
        if not space_desc:
            flash('공간 설명을 입력하세요.', 'error')
            return redirect(url_for('main.space.index'))
        
        if re.match(config.SPACE_DESC_RE, space_desc) is None:
            flash('공간 설명은 한글, 영문, 공백, 숫자만 사용하여 0~32자 사이여야 합니다.', 'error')
            return redirect(url_for('main.space.index'))
        
        if not find_allow_human and not find_notallow_human and not find_unknown_human:
            flash('작업 옵션을 선택하세요.', 'error')
            return redirect(url_for('main.space.index'))
        
        work_list = ['0', '1', '2', '3']
        if find_allow_human not in work_list or find_notallow_human not in work_list or find_unknown_human not in work_list:
            flash('작업 옵션이 올바르지 않습니다.', 'error')
            return redirect(url_for('main.space.index'))
        
        space_ctrl.create(space_name, space_desc, find_allow_human, find_notallow_human, find_unknown_human, session.get('user_info')['uuid'])
        flash('공간이 생성되었습니다.', 'success')
        return redirect(url_for('main.dashboard.index'))
    
    return render_template('space/make.html')

@bp.route('/remove/<space_uuid>', methods=['GET']) 
@login_required
def remove(space_uuid):
    user_uuid = session.get('user_info')['uuid']
    
    if not space_uuid:
        flash('공간을 선택하세요.', 'error')
        return redirect(url_for('main.dashboard.index'))
    
    if space_ctrl.remove(space_uuid, user_uuid):
        flash('공간이 삭제되었습니다.', 'success')
        return redirect(url_for('main.dashboard.index'))
    else:
        flash('공간을 삭제할 수 없습니다.', 'error')
        return redirect(url_for('main.dashboard.index'))

@bp.route('/regi_device', methods=['GET', 'POST'])
@login_required
def regi_device():
    if request.method == "POST":
        space_uuid = request.form.get('space-uuid')
        device_serial = request.form.get('device-serial')
        
        if not space_uuid:
            flash('공간을 선택하세요.', 'error')
            return redirect(url_for('main.dashboard.index'))
        
        if not device_serial:
            flash('장치를 선택하세요.', 'error')
            return redirect(url_for('main.dashboard.index'))
        
        if space_ctrl.regi_work_device(space_uuid, device_serial):
            flash('장치가 등록되었습니다.', 'success')
            return redirect(url_for('main.dashboard.index'))
        else:
            flash('장치를 등록할 수 없습니다.', 'error')
            return redirect(url_for('main.dashboard.index'))
    
    return render_template('space/regi_device.html', spaces=space_ctrl.get_db(), devices=device_ctrl.get_device_db())
