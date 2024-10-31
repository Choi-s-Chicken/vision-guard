import json
import os
import config

def get_space_db():
    with open(config.SPACE_DB_PATH, 'r') as f:
        space_db = json.load(f)
    return space_db

def remove_space_db(uuid):
    space_db = get_space_db()
    for i, space in enumerate(space_db):
        if space['uuid'] == uuid:
            del space_db[i]
            break
    with open(config.SPACE_DB_PATH, 'w') as f:
        json.dump(space_db, f, indent=4)
    os.rmdir(os.path.join(config.SPACE_DB_PATH, uuid))
        
def add_space_db(space_name, find_allow_human_work, find_notallow_human_work, find_unknown_human_work):
    space_db = get_space_db()
    uuid = os.urandom(16).hex()
    space_db.append({
        'uuid': uuid,
        'space_name': space_name,
        'space_path': os.path.join(config.SPACE_DB_PATH, uuid),
        'find_allow_human_work': find_allow_human_work,
        'find_notallow_human_work': find_notallow_human_work,
        'find_unknown_human_work': find_unknown_human_work
    })
    with open(config.SPACE_DB_PATH, 'w') as f:
        json.dump(space_db, f, indent=4)
        
    os.mkdir(space_db[-1]['space_path'])
    os.mkdir(os.path.join(space_db[-1]['space_path'], 'allow_human'))
    os.mkdir(os.path.join(space_db[-1]['space_path'], 'notallow_human'))
    os.mkdir(os.path.join(space_db[-1]['space_path'], 'capture'))