import json
import os
import shutil
import config
import src.utils as utils
import modules.auth as auth_ctrl
import modules.device as device_ctrl

def get_db():
    with open(config.SPACE_DB_PATH, 'r') as f:
        space_db = json.load(f)
    return space_db

def verify_space_uuid(_space_uuid):
    space_db = get_db()
    for space in space_db:
        if space['uuid'] == _space_uuid:
            return True
    return False

def create(_space_name, _space_desc, _find_allow_human_work, _find_notallow_human_work, _find_unknown_human_work, _owner_uuid):
    space_db = get_db()
    uuid = os.urandom(16).hex()
    space_db.append({
        'uuid': uuid,
        'name': _space_name,
        'description': _space_desc,
        'path': os.path.join(config.SPACE_PATH, uuid),
        'owner_uuid': _owner_uuid,
        'create_time': utils.get_now_ftime(),
        'find_allow_human_work': _find_allow_human_work,
        'find_notallow_human_work': _find_notallow_human_work,
        'find_unknown_human_work': _find_unknown_human_work,
        'find_human_alert_mode': False,
        "work_device_uuids": []
    })
    with open(config.SPACE_DB_PATH, 'w') as f:
        json.dump(space_db, f, indent=4)
        
    os.mkdir(space_db[-1]['path'])
    os.mkdir(os.path.join(space_db[-1]['path'], 'allow_human'))
    os.mkdir(os.path.join(space_db[-1]['path'], 'notallow_human'))
    os.mkdir(os.path.join(space_db[-1]['path'], 'capture'))

def remove(_uuid, _owner_uuid):    
    space_db = get_db()
    for i, space in enumerate(space_db):
        if space['uuid'] == _uuid:
            if space['owner_uuid'] != _owner_uuid:
                return False
            del space_db[i]
            break
    with open(config.SPACE_DB_PATH, 'w') as f:
        json.dump(space_db, f, indent=4)
    shutil.rmtree(os.path.join(config.SPACE_PATH, _uuid))
    device_ctrl.remove_work_space_uuid(_uuid)
    
    return True

def regi_work_device(_space_serial, _device_uuid):
    space_db = get_db()
    for space in space_db:
        if space['uuid'] == _space_serial:
            # duplicate check
            for work_device_uuid in space['work_device_uuids']:
                if work_device_uuid == _device_uuid:
                    return False
            
            if device_ctrl.set_device_work_space_uuid(_device_uuid, _space_serial) == False:
                return False
            
            space['work_device_uuids'].append(_device_uuid)
            break
    with open(config.SPACE_DB_PATH, 'w') as f:
        json.dump(space_db, f, indent=4)
    return True

def remove_work_device(_space_uuid, _device_uuid):
    space_db = get_db()
    
    if verify_space_uuid(_space_uuid) == False:
        return False
    
    for space in space_db:
        for space_work_device_uuid in space['work_device_uuids']:
            if space_work_device_uuid == _device_uuid:
                space['work_device_uuids'].remove(_device_uuid)
                break
    with open(config.SPACE_DB_PATH, 'w') as f:
        json.dump(space_db, f, indent=4)
    
    device_ctrl.remove_work_space_uuid(_space_uuid)
    return True

def remove_work_device_all(_device_uuid):
    space_db = get_db()
    for space in space_db:
        for space_work_device_uuid in space['work_device_uuids']:
            if space_work_device_uuid == _device_uuid:
                space['work_device_uuids'].remove(_device_uuid)
    with open(config.SPACE_DB_PATH, 'w') as f:
        json.dump(space_db, f, indent=4)
    return True