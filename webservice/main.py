import secrets
import config
from flask import Flask, flash, render_template, redirect, url_for, request, session, jsonify
from webservice.auth import change_password, login_required, check_login, del_account
import webservice.router.main as router
import src.utils as utils
from modules.logging import logger

class VGApp():
    def __init__(self):
        self.application = Flask(import_name=__name__)
        self.application.secret_key = secrets.token_hex(32)
        self.application.register_blueprint(router.bp)
        
        # main route
        @self.application.route('/')
        @login_required
        def home():
            return render_template("index.html", prct_model=config.PRCT_MODEL, prct_serial=config.PRCT_SERIAL,
                                   status=config.get_config('status'), alarm=config.get_config('alarm'), status_normal=config.STATUS_NORMAL,
                                   status_warn=config.STATUS_WARN, status_error=config.STATUS_ERROR, status_criti=config.STATUS_CRITI,
                                   client_name=session.get('username'), reboot_poss=config.get_config('reboot_poss'), alarm_poss=config.get_config('alarm_poss'),
                                   last_server_connect_time=config.get_config('last_server_connect_time'))

        @self.application.route('/vgdevicegetinfo')
        def vgdevicegetinfo():
            res_data = {
                "model": config.PRCT_MODEL,
                "is_vgdevice": True
            }
            return jsonify(res_data)
        
        @self.application.route('/login', methods=['GET', 'POST'])
        def login():
            if 'username' in session:
                flash('이미 로그인되어 있습니다.', 'warning')
                return redirect(url_for('home'), 302)
            
            if request.method == 'POST':
                _input_id = request.form.get('userid')
                _input_pw = request.form.get('userpw')
                
                if not _input_id or not _input_pw:
                    flash("로그인 실패: 아이디와 비밀번호를 입력해주세요.", "error")
                    return render_template('login.html', client_ip=utils.get_client_ip(request), client_name=session.get('username')), 401

                # (NAME, LEVEL)
                login_rst = check_login(_input_id, _input_pw)
                if login_rst != False:
                    if (login_rst[1] in [0, 1]) == False:
                        flash("로그인 실패: 권한이 없습니다.", "error")
                        return render_template('login.html', client_ip=utils.get_client_ip(request), client_name=session.get('username')), 401
                    
                    session['userid'] = _input_id
                    session['username'] = login_rst[0]
                    session['userlevel'] = login_rst[1]
                    
                    flash(f"({session.get('userid')}) 로그인되었습니다.", 'success')
                    return redirect(url_for('home'), 302)
                else:
                    flash("로그인 실패: 아이디 또는 비밀번호가 일치하지 않습니다.", "error")
                    return render_template('login.html', client_ip=utils.get_client_ip(request), client_name=session.get('username')), 401

            return render_template('login.html', client_ip=utils.get_client_ip(request), client_name=session.get('username'))

        @self.application.route('/logout', methods=['GET'])
        @login_required
        def logout():
            flash(f"({session.get('userid')}) 로그아웃되었습니다.", 'warning')
            session.pop('userid', None)
            session.pop('username', None)
            session.pop('userlevel', None)
            return redirect(url_for('login'), 302)

        @self.application.route('/changepw', methods=['GET', 'POST'])
        @login_required
        def changepw():
            if request.method == 'POST':
                old_pw = request.form.get('old-pw')
                new_pw = request.form.get('new-pw')
                user_id = session.get('userid')

                if not old_pw or not new_pw:
                    logger.error(f"비밀번호 변경 실패: 모든 입력란을 입력해주세요. ({user_id})")
                    flash("비밀번호 변경 실패: 모든 입력란을 입력해주세요.", "error")
                    return render_template('changepw.html', client_ip=utils.get_client_ip(request)), 400

                if not check_login(user_id, old_pw):
                    logger.error(f"비밀번호 변경 실패: 기존 비밀번호가 일치하지 않습니다. ({user_id})")
                    flash("비밀번호 변경 실패: 기존 비밀번호가 일치하지 않습니다.", "error")
                    return render_template('changepw.html', client_ip=utils.get_client_ip(request)), 400

                change_password(user_id, new_pw)
                logger.info(f"비밀번호 변경 성공: 비밀번호가 성공적으로 변경되었습니다. ({user_id})")
                flash("비밀번호가 성공적으로 변경되었습니다. 다시 로그인하세요.", "success")
                
                session.clear()
                self.application.secret_key = secrets.token_hex(32)
                
                return redirect(url_for('login')), 302

            return render_template('changepw.html', client_ip=utils.get_client_ip(request), client_name=session.get('username')), 200

        # error handlers
        @self.application.errorhandler(404)
        def error_404(e):
            return render_template('error/404.html', client_ip=utils.get_client_ip(request), client_name=session.get('username')), 404

        @self.application.errorhandler(405)
        def error_405(e):
            return render_template('error/405.html', client_ip=utils.get_client_ip(request), client_name=session.get('username')), 405

    def run(self, _host, _port, _debug=False):
        self.application.run(_host, _port, debug=_debug)