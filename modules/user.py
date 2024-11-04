import os
import json
import config
import src.utils as utils
import modules.space as space_ctrl

def get_user_db():
    with open(config.USER_DB_PATH, 'r') as f:
        return json.load(f)
    
def set_user_db(_user_db):
    with open(config.USER_DB_PATH, 'w') as f:
        json.dump(_user_db, f, indent=4)

def add_user(_user_id, _user_pw, _user_name):
    user_db = get_user_db()
    user_db.append({
        'user_id': _user_id,
        'user_pw': _user_pw,
        'user_name': _user_name,
        'uuid': os.urandom(16).hex(),
        'regi_date': utils.get_now_ftime()
    })
    set_user_db(user_db)
    
def remove_user(_user_id):
    user_db = get_user_db()
    for i, user in enumerate(user_db):
        if user['user_id'] == _user_id:
            del user_db[i]
            break
    
    set_user_db(user_db)
    
def set_user(_user_id, _user_pw, _user_name):
    user_db = get_user_db()
    for i, user in enumerate(user_db):
        if user['user_id'] == _user_id:
            user_db[i]['user_pw'] = _user_pw
            user_db[i]['user_name'] = _user_name
            break
    set_user_db(user_db)