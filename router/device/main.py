import base64
import os
from flask import Blueprint, flash, redirect, render_template, request, jsonify, send_file, session, url_for
import config
from modules.auth import login_required
from modules.FaceRecognition import FaceRecognition

bp = Blueprint('device', __name__, url_prefix='/device')

ai = FaceRecognition(config.FACE_DECT_MODEL_PATH, config.FACE_REID_MODEL_PATH)

@bp.route('/manage/<string:prct_serial>', methods=['GET', 'POST'])
@login_required
def manage(prct_serial):
    for prct in config.get_products_db():
        if prct['serial'] != prct_serial:
            continue
            
        if prct['owner_uuid'] == session['user_info']['uuid']:
            return render_template('device/manage.html', user_info=session.get('user_info'), prct=prct)
    
    return render_template('error/404.html', )

@bp.route('/get-image', methods=['GET'])
def get_image():
    image_path = os.path.join('./db', 'captures', "a6bd8024", f"now_capture.jpg")
    output_path = os.path.join('./db', 'captures', "a6bd8024", f"output_capture.jpg")   
    
    return send_file(output_path, mimetype='image/jpeg', cache_timeout=0)

@bp.route('/image-process', methods=['POST'])
def image_process():
    res_data = request.json
    
    print(res_data['capture_time'])
    
    # 이미지 저장 경로 설정
    image_path = os.path.join('./db', 'captures', res_data['serial'], f"now_capture.jpg")
    output_path = os.path.join('./db', 'captures', res_data['serial'], f"output_capture.jpg")
    with open(image_path, 'wb') as f:
        f.write(base64.b64decode(res_data['capture_data']))
        
    # 이미지 처리
    ai.annotate_faces(image_path, output_path, 0.1)
    
    return jsonify({'status': 'success', 'message': '이미지가 성공적으로 업로드되었습니다.'}), 200

@bp.route('/userregi', methods=['GET', 'POST'])
@login_required
def userregi():
    if request.method == 'POST':
        prct_serial = request.form.get('prct-serial')
        
        if not prct_serial:
            flash('시리얼 번호를 입력하세요.', 'error')
            return redirect(url_for('main.device.userregi'))
        
        prct_db = config.get_products_db()
        search_db = prct_db
        for index, prct in enumerate(search_db):
            if prct['serial'] == prct_serial:
                if prct['owner_uuid'] is not None:
                    flash('이미 등록된 장치입니다.', 'error')
                    return redirect(url_for('main.device.userregi'))

                prct_db[index]['owner_uuid'] = session['user_info']['uuid']
                config.set_products_db(prct_db)
                flash('장치가 계정에 등록되었습니다.', 'success')
                return redirect(url_for('main.dashboard.index'))
        
        flash('잘못된 시리얼키입니다. 확인 후 다시 등록하세요.', 'error')
        return redirect(url_for('main.device.userregi'))
    
    return render_template('device/userregi.html', user_info=session.get('user_info'))

@bp.route('/userunregi', methods=['GET', 'POST'])
@login_required
def userunregi():
    if request.method == 'POST':
        prct_serial = request.form.get('prct-serial')
        
        if not prct_serial:
            flash('시리얼 번호를 입력하세요.', 'error')
            return redirect(url_for('main.device.userunregi'))
        
        prct_db = config.get_products_db()
        search_db = prct_db
        for index, prct in enumerate(search_db):
            if prct['serial'] == prct_serial:
                if prct['owner_uuid'] is None:
                    flash('등록되지 않은 장치입니다.', 'error')
                    return redirect(url_for('main.device.userunregi'))

                if prct['owner_uuid'] == session['user_info']['uuid']:
                    prct_db[index]['owner_uuid'] = None
                    config.set_products_db(prct_db)
                    flash('장치가 계정에서 해제되었습니다.', 'success')
                    return redirect(url_for('main.dashboard.index'))
                
                flash('자신의 장치만 해지할 수 있습니다.', 'success')
                return redirect(url_for('main.dashboard.index'))
        
        flash('잘못된 시리얼키입니다. 확인 후 다시 등록하세요.', 'error')
        return redirect(url_for('main.device.userunregi'))
    
    return render_template('device/userunregi.html', user_info=session.get('user_info'))