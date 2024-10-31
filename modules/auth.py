from functools import wraps
from flask import session, redirect, url_for, flash
from datetime import timedelta
import sqlite3
import base64
import config
import src.utils as utils

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_info' not in session:
            flash('로그인 후 이용하세요.', 'warning')
            return redirect(url_for('main.user.login'))
        
        user_info = session.get('user_info')
        
        if check_account(user_info.get('user_id'), user_info.get('user_pw'), False) == False:
            session.clear()
            flash('로그인 정보가 올바르지 않습니다. 다시 로그인하세요.', 'error')
            return redirect(url_for('main.user.login'))
        
        if 'lastworktime' in session:
            if utils.convert_now_ftime(session['lastworktime']) < utils.convert_now_ftime(utils.get_now_ftime()) - timedelta(minutes=3):
                session.clear()
                flash('세션이 만료되었습니다. 다시 로그인하세요.', 'error')
                return redirect(url_for('main.user.login'))
        
        session['lastworktime'] = utils.get_now_ftime()
        
        return f(*args, **kwargs)
    return decorated_function

def check_id_duplicate(_user_id):
    for db_user in config.get_user_db():
        if db_user['user_id'] == _user_id:
            return db_user
    return False

def check_account(_user_id, _user_pw, _hashing_check=True):
    for db_user in config.get_user_db():
        if db_user['user_id'] == _user_id and db_user['user_pw'] == utils.gen_hash(_user_pw) if _hashing_check else _user_pw:
            return db_user
    return False

def regi_account(_user_id, _user_pw, _user_name, _uuid=utils.gen_rhash()):
    data = config.get_user_db()
    regi_data = {
        'user_id': _user_id,
        'user_pw': utils.gen_hash(_user_pw),
        'user_name': _user_name,
        'uuid': _uuid,
        'regi_date': utils.get_now_ftime()
    }
    
    data.append(regi_data)
    config.set_user_db(data)