import secrets
import config
from flask import Flask, flash, render_template, redirect, url_for, request, session
from webservice.auth import login_required, check_login
import webservice.router.main as router
import src.utils as utils

class VGApp():
    def __init__(self, _host, _port, _debug=False):
        self._host = _host
        self._port = _port
        self._debug = _debug
        
        self.application = Flask(import_name=__name__)
        self.application.secret_key = secrets.token_hex(32)
        self.application.register_blueprint(router.bp)

        # main route
        @self.application.route('/')
        @login_required
        def home():
            return render_template("index.html", prct_model=config.PRCT_MODEL, prct_serial=config.PRCT_SERIAL,
                                   status=config.get_config('status'), status_normal=config.STATUS_NORMAL, status_warn=config.STATUS_WARN,
                                   status_error=config.STATUS_ERROR, status_criti=config.STATUS_CRITI)
            

        @self.application.route('/login', methods=['GET', 'POST'])
        def login():
            if 'username' in session:
                flash('이미 로그인되어 있습니다.', 'warning')
                return render_template('index.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                                       client_name=session.get('username')), 200
            
            if request.method == 'POST':
                _input_id = request.form.get('userid')
                _input_pw = request.form.get('userpw')
                
                if not _input_id or not _input_pw:
                    flash("로그인 실패: 아이디와 비밀번호를 입력해주세요.", "error")
                    return render_template('login.html', client_ip=utils.get_client_ip(request)), 401

                # (NAME, LEVEL)
                login_rst = check_login(_input_id, _input_pw)
                if login_rst != False:
                    if (login_rst[1] in [0, 1]) == False:
                        flash("로그인 실패: 권한이 없습니다.", "error")
                        return render_template('login.html', client_ip=utils.get_client_ip(request)), 401
                    
                    session['userid'] = _input_id
                    session['username'] = login_rst[0]
                    session['userlevel'] = login_rst[1]
                    
                    flash(f"({session.get('userid')}) 로그인되었습니다.", 'success')
                    return render_template('index.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                                            client_name=session.get('username')), 200
                else:
                    flash("로그인 실패: 아이디 또는 비밀번호가 일치하지 않습니다.", "error")
                    return render_template('login.html', client_ip=utils.get_client_ip(request)), 401

            return render_template('login.html', client_ip=utils.get_client_ip(request))

        @self.application.route('/logout', methods=['GET'])
        @login_required
        def logout():
            flash(f"({session.get('userid')}) 로그아웃되었습니다.", 'warning')
            session.pop('userid', None)
            session.pop('username', None)
            session.pop('userlevel', None)
            return redirect(url_for('login'), 302)

        @self.application.route('/보름달', methods=['GET'])
        def ddalbae():
            user_id = session.get('userid')
            
            if 'username' not in session:
                return render_template('error/404.html', client_ip=utils.get_client_ip(request))
            
            # if user_id in utils.SPECIAL_USERID:
                # return render_template('index_secret.html'), 200
            # return render_template('error/404.html', client_ip=utils.get_client_ip(request)), 404

            return render_template('index_secret.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                                client_name=session.get('username')), 200

        # error handlers
        @self.application.errorhandler(404)
        def error_404(e):
            return render_template('error/404.html', client_ip=utils.get_client_ip(request)), 404

        @self.application.errorhandler(405)
        def error_405(e):
            return render_template('error/405.html', client_ip=utils.get_client_ip(request)), 405

    def run(self):
        self.application.run(self._host, self._port, debug=self._debug)