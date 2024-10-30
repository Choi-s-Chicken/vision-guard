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
        if 'username' not in session:
            flash('로그인 후 이용하세요.', 'warning')
            return redirect(url_for('login'))
        
        user_id = session.get('userid')
        
        is_id_exist = False
        for db_user in config.get_user_db():
            if db_user['login_id'] == user_id:
                is_id_exist = True
                break
        
        if is_id_exist == False:
            session.clear()
            flash('존재하지 않는 계정입니다. 다시 로그인하세요.', 'error')
            return redirect(url_for('login'))
        
        if 'lastworktime' in session:
            if utils.convert_now_ftime(session['lastworktime']) < utils.convert_now_ftime(utils.get_now_ftime()) - timedelta(minutes=5):
                session.clear()
                flash('세션이 만료되었습니다. 다시 로그인하세요.', 'error')
                return redirect(url_for('login'))
        
        session['lastworktime'] = utils.get_now_ftime()
        
        return f(*args, **kwargs)
    return decorated_function

def (user_id):