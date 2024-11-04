import base64
import os
from flask import Blueprint, flash, redirect, render_template, request, jsonify, send_file, session, url_for
import config
from modules.auth import login_required
from modules.FaceRecognition import FaceRecognition
import modules.device as device_ctrl
import modules.space as space_ctrl
import src.utils as utils


bp = Blueprint('device', __name__, url_prefix='/device')
ai = FaceRecognition(config.FACE_DECT_MODEL_PATH, config.FACE_REID_MODEL_PATH)

@bp.route('/manage/<string:prct_serial>', methods=['GET'])
@login_required
def manage(prct_serial):
    is_owner = False
    for prct in device_ctrl.get_device_db():
        if prct['serial'] != prct_serial:
            continue
            
        if prct['owner_uuid'] == session['user_info']['uuid']:
            is_owner = True
            break
    
    if is_owner == False:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('main.dashboard.index'))
    
    prct_reboot_poss = request.args.get('reboot_poss', '-999')
    prct_alarm_poss = request.args.get('alarm_poss', '-999')
    prct_alarm = request.args.get('alarm', '-999')
    prct_alarm_disable = request.args.get('alarm_disable', '-999')
    
    if prct_reboot_poss != '-999':
        if prct_reboot_poss not in ['false', 'true']:
            flash('올바르지 않은 값입니다.', 'error')
            return redirect(url_for('main.device.manage', prct_serial=prct_serial))
        
        if prct_reboot_poss == 'true':
            device_ctrl.set_device_reboot_poss(prct_serial, True)
        else:
            device_ctrl.set_device_reboot_poss(prct_serial, False)
        flash('재부팅 가능 여부가 변경되었습니다.', 'success')
        return redirect(url_for('main.device.manage', prct_serial=prct_serial))
        
    if prct_alarm_poss != '-999':
        if prct_alarm_poss not in ['false', 'true']:
            flash('올바르지 않은 값입니다.', 'error')
            return redirect(url_for('main.device.manage', prct_serial=prct_serial))
        
        if prct_alarm_poss == 'true':
            device_ctrl.set_device_alarm_poss(prct_serial, True)
        else:
            device_ctrl.set_device_alarm_poss(prct_serial, False)
        flash('경보 가능 여부가 변경되었습니다.', 'success')
        return redirect(url_for('main.device.manage', prct_serial=prct_serial))
        
    if prct_alarm != '-999':
        if prct_alarm not in ['false', 'true']:
            flash('올바르지 않은 값입니다.', 'error')
            return redirect(url_for('main.device.manage', prct_serial=prct_serial))
        
        if prct_alarm == 'true':
            device_ctrl.set_device_alarm(prct_serial, True)
            device_ctrl.set_device_alarm_disable(prct_serial, False)
            flash('경보를 울렸습니다.', 'success')
        else:
            device_ctrl.set_device_alarm(prct_serial, False)
            device_ctrl.set_device_alarm_disable(prct_serial, True)
        return redirect(url_for('main.device.manage', prct_serial=prct_serial))
    
    if prct_alarm_disable != '-999':
        if prct_alarm_disable not in ['false', 'true']:
            flash('올바르지 않은 값입니다.', 'error')
            return redirect(url_for('main.device.manage', prct_serial=prct_serial))
        
        if prct_alarm_disable == 'true':
            device_ctrl.set_device_alarm(prct_serial, False)
            device_ctrl.set_device_alarm_disable(prct_serial, True)
            flash('경보를 껏습니다.', 'success')
        else:
            device_ctrl.set_device_alarm_disable(prct_serial, True)
            device_ctrl.set_device_alarm(prct_serial, False)
        return redirect(url_for('main.device.manage', prct_serial=prct_serial))
    
    return render_template('device/manage.html', user_info=session.get('user_info'), prct=prct)

@bp.route('/get-image', methods=['GET'])
def get_image():
    req_user_uuid = request.args.get('req_user_uuid', '-999')
    prct_serial = request.args.get('prct_serial', '-999')
    
    if '-999' in [req_user_uuid, prct_serial]:
        return jsonify({'status': 'error', 'message': 'Require parameter missing'}), 400
    
    if device_ctrl.verify_device_serial(prct_serial) is False:
        return jsonify({'status': 'error', 'message': 'Invaild device'}), 400
    
    prct_db = device_ctrl.get_device_db()
    
    is_owner = False
    for prct in prct_db:
        if prct['serial'] == prct_serial:
            if prct['owner_uuid'] == req_user_uuid:
                is_owner = True
                break
    if is_owner is False:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 400
    
    image_path = os.path.join('./db', 'captures', prct_serial, f"output_capture.jpg")   
    
    return send_file(image_path, mimetype='image/jpeg', cache_timeout=0)

@bp.route('/get-status', methods=['GET'])
def get_status():
    res_data = request.json
    
    prct_serial = res_data.get('serial', '-999')
    prct_connect_key = res_data.get('connect_key', '-999')
    
    if '-999' in [prct_serial, prct_connect_key]:
        return jsonify({'status': 'error', 'message': 'Require parameter missing'}), 400
    
    if device_ctrl.verify_device(prct_serial, prct_connect_key) is False:
        return jsonify({'status': 'error', 'message': 'Invaild device'}), 400
    
    prct_db = device_ctrl.get_device_db()
    for prct in prct_db:
        if prct['serial'] == prct_serial:
            return jsonify({'status': 'success', 'message': 'Success', 'server_device_status': prct}), 200
    

@bp.route('/data-process', methods=['POST'])
def data_process():
    res_data = request.json
    
    device_serial = res_data.get('serial', '-999')
    device_connect_key = res_data.get('connect_key', '-999')
    device_status = res_data.get('status', '-999')
    device_is_alarm = res_data.get('is_alarm', '-999')
    device_reboot_poss = res_data.get('reboot_poss', '-999')
    device_alarm_poss = res_data.get('alarm_poss', '-999')
    device_capture_time = res_data.get('capture_time', '-999')
    device_capture_data = res_data.get('capture_data', '-999')
    
    if '-999' in [device_serial, device_connect_key, device_status, device_is_alarm, device_reboot_poss, device_alarm_poss, device_capture_time, device_capture_data]:
        return jsonify({'status': 'error', 'message': 'Require parameter missing'}), 400
    
    if device_ctrl.verify_device(device_serial, device_connect_key) is False:
        print(device_serial, device_connect_key)
        return jsonify({'status': 'error', 'message': 'Invaild device'}), 400
    
    device_ctrl.set_device_status(device_serial, device_status)
    
    # 이미지 저장 경로 설정
    base_path = os.path.join('./db', 'captures', device_serial)
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    image_path = os.path.join(base_path, f"{utils.get_now_ftime()}now_capture.jpg")
    output_path = os.path.join(base_path, f"{utils.get_now_ftime()}output_capture.jpg")
    with open(image_path, 'wb') as f:
        f.write(base64.b64decode(res_data['capture_data']))
    
    # 이미지 처리
    ai.annotate_faces(image_path, output_path, res_data['capture_time'], 0.3)
    
    return jsonify({'status': 'success', 'message': 'Success'}), 200

@bp.route('/userregi', methods=['GET', 'POST'])
@login_required
def userregi():
    if request.method == 'POST':
        prct_serial = request.form.get('prct-serial')
        
        if not prct_serial:
            flash('시리얼 번호를 입력하세요.', 'error')
            return redirect(url_for('main.device.userregi'))
        
        if device_ctrl.verify_device_serial(prct_serial) is False:
            flash('잘못된 시리얼키입니다. 시리얼키를 확인하세요.', 'error')
            return redirect(url_for('main.device.userregi'))
        
        prct_db = device_ctrl.get_device_db()
        search_db = prct_db
        for index, prct in enumerate(search_db):
            if prct['serial'] == prct_serial:
                if prct['owner_uuid'] is not None:
                    flash('이미 등록된 장치입니다.', 'error')
                    return redirect(url_for('main.device.userregi'))

                prct_db[index]['owner_uuid'] = session['user_info']['uuid']
                device_ctrl.set_device_db(prct_db)
                flash('장치가 계정에 등록되었습니다.', 'success')
                return redirect(url_for('main.dashboard.index'))

    return render_template('device/userregi.html', user_info=session['user_info'])

@bp.route('/userunregi', methods=['GET', 'POST'])
@login_required
def userunregi():
    if request.method == 'POST':
        prct_serial = request.form.get('prct-serial')
        
        if not prct_serial:
            flash('시리얼 번호를 입력하세요.', 'error')
            return redirect(url_for('main.device.userunregi'))
        
        if device_ctrl.verify_device_serial(prct_serial) is False:
            flash('잘못된 시리얼키입니다. 시리얼키를 확인하세요.', 'error')
            return redirect(url_for('main.device.userunregi'))
        
        prct_db = device_ctrl.get_device_db()
        search_db = prct_db
        for index, prct in enumerate(search_db):
            if prct['serial'] == prct_serial:
                if prct['owner_uuid'] is None:
                    flash('등록되지 않은 장치입니다.', 'error')
                    return redirect(url_for('main.device.userunregi'))

                if prct['owner_uuid'] == session['user_info']['uuid']:
                    prct_db[index]['owner_uuid'] = None
                    device_ctrl.set_device_db(prct_db)
                    flash('장치가 계정에서 제거되었습니다.', 'success')
                    return redirect(url_for('main.dashboard.index'))
                
                flash('자신의 장치만 해지할 수 있습니다.', 'success')
                return redirect(url_for('main.dashboard.index'))
        
        flash('잘못된 시리얼키입니다. 확인 후 다시 등록하세요.', 'error')
        return redirect(url_for('main.device.userunregi'))
    
    return render_template('device/userunregi.html', user_info=session.get('user_info'), regi_prcts=device_ctrl.get_device_db())

@bp.route('/work-space-unregi', methods=['GET'])
@login_required
def work_space_unregi():
    device_serial = request.args.get('prct_serial')
    
    if not device_serial:
        flash('잘못된 요청입니다.', 'error')
        return redirect(url_for('main.dashboard.index'))
    
    if device_ctrl.verify_device_serial(device_serial) is False:
        flash('잘못된 시리얼키입니다. 시리얼키를 확인하세요.', 'error')
        return redirect(url_for('main.dashboard.index'))
    
    if space_ctrl.remove_work_device_all(device_serial) is False:
        flash('공간에서 장치를 제거하는데 실패했습니다.', 'error')
        
    device_ctrl.remove_work_space(device_serial)
    
    flash('공간에서 장치를 제거했습니다.', 'success')
    return redirect(url_for('main.dashboard.index'))