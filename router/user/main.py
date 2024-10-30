import re
from flask import Blueprint, flash, redirect, render_template, request, jsonify, session, url_for
import config
from modules.auth import login_required
import modules.auth as auth
import src.utils as utils

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    if request.method == 'POST':
        username = request.form.get('username')
        userid = request.form.get('userid')
        userpw = request.form.get('userpw')
        new_userpw = request.form.get('newuserpw')
        new_userpw_re = request.form.get('newuserpwre')
        
        org_data = auth.check_id_duplicate(session['user_info']['user_id'])
        set_data = org_data.copy()
        
        if re.match(config.USER_NM_RE, username) is None:
            flash('이름은 1~8자 사이 한글로만 입력해주세요.', 'error')
            return redirect(url_for('main.user.setting'))
        if re.match(config.USER_ID_RE, userid) is None:
            flash('아이디는 2~16자 사이 영문 대소문자와 숫자로만 입력해주세요.', 'error')
            return redirect(url_for('main.user.setting'))
        if re.match(config.USER_PW_RE, userpw) is None:
            flash('비밀번호는 8자~256자 사이 영문 대소문자, 숫자, 특수문자를 모두 포함해야 합니다.', 'error')
            return redirect(url_for('main.user.setting'))
        if new_userpw != new_userpw_re:
            flash('새 비밀번호가 일치하지 않습니다.', 'error')
            return redirect(url_for('main.user.setting'))
        if new_userpw and re.match(config.USER_PW_RE, new_userpw) is None:
            flash('새 비밀번호는 8자~256자 사이 영문 대소문자, 숫자, 특수문자를 모두 포함해야 합니다.', 'error')
            return redirect(url_for('main.user.setting'))
        
        if not auth.check_account(org_data['user_id'], userpw):
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return redirect(url_for('main.user.setting'))
        
        if auth.check_id_duplicate(userid) and userid != org_data['user_id']:
            flash('이미 존재하는 아이디입니다. 다른 아이디를 입력하세요.', 'error')
            return redirect(url_for('main.user.setting'))
        
        set_data['user_id'] = userid
        set_data['user_name'] = username
        if new_userpw:
            set_data['user_pw'] = utils.gen_hash(new_userpw)
        
        user_db = config.get_user_db()
        for index, db_user in enumerate(user_db):
            if db_user['user_id'] == org_data['user_id']:
                user_db[index] = set_data
                break
        config.set_user_db(user_db)
                
        session['user_info'] = set_data
        flash('정보가 수정되었습니다.', 'info')
        return redirect(url_for('main.user.setting'))
    
    return render_template('user/setting.html', user_info=session.get('user_info'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_info' in session:
        flash("이미 로그인되어 있습니다.", 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        userid = request.form.get('userid')
        userpw = request.form.get('userpw')
        
        account_check_rst = auth.check_account(userid, userpw)
        if account_check_rst == False:
            flash('아이디 또는 비밀번호가 일치하지 않습니다.', 'error')
            return redirect(url_for('main.user.login'))
        
        session['user_info'] = account_check_rst
        
        return redirect(url_for('main.index'))
            
    
    return render_template('user/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_info' in session:
        flash("이미 로그인되어 있습니다.", 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        userid = request.form.get('userid')
        userpw = request.form.get('userpw')
        
        if auth.check_id_duplicate(userid) == True:
            flash('이미 존재하는 아이디입니다.', 'error')
            return redirect(url_for('main.user.register'))
        
        if re.match(config.USER_NM_RE, username) == None:
            flash('이름은 1~8자 사이 한글로만 입력해주세요.', 'error')
            return redirect(url_for('main.user.register'))
        if re.match(config.USER_ID_RE, userid) == None:
            flash('아이디는 2~16자 사이 영문 대소문자와 숫자로만 입력해주세요.', 'error')
            return redirect(url_for('main.user.register'))
        if re.match(config.USER_PW_RE, userpw) == None:
            flash('비밀번호는 8자~256자 사이 영문 대소문자, 숫자, 특수문자를 모두 포함해야 합니다.', 'error')
            return redirect(url_for('main.user.register'))
        
        if auth.regi_account(userid, userpw, username) == False:
            flash('일시적인 오류입니다. 나중에 다시 시도하세요.', 'error')
            return redirect(url_for('main.user.register'))
        
        flash('회원가입이 완료되었습니다.', 'info')
        return redirect(url_for('main.index'))
    
    return render_template('user/register.html')

@bp.route('/logout', methods=['GET'])
@login_required
def logout():
    flash(f"({session['user_info']['user_id']}) 로그아웃 되었습니다.", 'info')
    session.clear()
    return redirect(url_for('main.index'))