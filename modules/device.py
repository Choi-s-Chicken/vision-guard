import json
import os
import base64
import config
import src.utils as utils
import modules.space as space_ctrl

def get_device_db():
    with open(os.path.join(config.DEVICE_DB_PATH), 'r') as f:
        return json.load(f)

def set_device_db(_prct_db):
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(_prct_db, f)

def regi_device_owner(_serial, _owner_uuid):
    data = get_device_db()
    for index, device in enumerate(data):
        if device['serial'] == _serial:
            data[index]['owner_uuid'] = _owner_uuid
            break
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(data, f)
        
def remove_device_owner(_owner_uuid):
    data = get_device_db()
    for index, device in enumerate(data):
        if device['owner_uuid'] == _owner_uuid:
            data[index]['owner_uuid'] = None
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(data, f)
    remove_device_owner(_owner_uuid)

def remove_work_space_uuid(_work_space_uuid):
    if space_ctrl.verify_space_uuid(_work_space_uuid) == False:
        return False
    
    data = get_device_db()
    for index, device in enumerate(data):
        if device['work_space_uuid'] == _work_space_uuid:
            data[index]['work_space_uuid'] = None
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(data, f)
    return True

def remove_work_space(_device_serial):
    data = get_device_db()
    for index, device in enumerate(data):
        if device['serial'] == _device_serial:
            data[index]['work_space_uuid'] = None
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(data, f)

def verify_device_serial(_serial):
    data = get_device_db()
    for device in data:
        if device['serial'] == _serial:
            return True
    return False

def verify_device(_serial, _connect_key):
    data = get_device_db()
    for device in data:
        if device['serial'] == _serial:
            if device['connect_key'] == _connect_key:
                return True
            else:
                break
    return False

def set_device_status(_serial, _status):
    data = get_device_db()
    for index, device in enumerate(data):
        if device['serial'] == _serial:
            data[index]['status'] = _status
            data[index]['last_connection'] = utils.get_now_ftime()
            break
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(data, f)
        
def set_device_reboot_poss(_serial, _reboot_poss):
    data = get_device_db()
    for index, device in enumerate(data):
        if device['serial'] == _serial:
            data[index]['reboot_possible'] = _reboot_poss
            break
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(data, f)
        
def set_device_alarm_poss(_serial, _alarm_poss):
    data = get_device_db()
    for index, device in enumerate(data):
        if device['serial'] == _serial:
            data[index]['alarm_possible'] = _alarm_poss
            break
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(data, f)
        
def set_device_alarm(_serial, _alarm):
    data = get_device_db()
    for index, device in enumerate(data):
        if device['serial'] == _serial:
            data[index]['alarm'] = _alarm
            break
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(data, f)
        
def set_device_alarm_disable(_serial, _alarm_disable):
    data = get_device_db()
    for index, device in enumerate(data):
        if device['serial'] == _serial:
            data[index]['alarm_disable'] = _alarm_disable
            break
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(data, f)
    

def set_device_work_space_uuid(_serial, _work_space_uuid):
    data = get_device_db()
    for index, device in enumerate(data):
        if device['serial'] == _serial:
            if device['work_space_uuid'] != None:
                return False
            data[index]['work_space_uuid'] = _work_space_uuid
            break
    with open(os.path.join(config.DEVICE_DB_PATH), 'w') as f:
        json.dump(data, f)
    return True