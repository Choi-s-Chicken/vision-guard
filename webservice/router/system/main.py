import threading
import config
import src.utils as utils
from flask import Blueprint, flash, render_template, redirect, url_for, request, session
from webservice.auth import login_required, check_login
import modules.targets as targets

bp = Blueprint('system', __name__, url_prefix='/system')

@bp.route("/reboot", methods=["GET"])
@login_required
def reboot():
    reboot_status = True
    detail = ""
    if config.get_config('status') == config.STATUS_WARN:
        reboot_status = False
        detail = "경보기가 작동 중일 때는 재부팅할 수 없습니다."
        return render_template("reboot.html", reboot_status=reboot_status, detail=detail)
    elif config.get_config('reboot_poss') == False:
        reboot_status = False
        detail = "재부팅이 비활성화 되어있습니다. 재부팅할 수 없습니다."
        return render_template("reboot.html", reboot_status=reboot_status, detail=detail)
    
    if reboot_status == True:
        threading.Thread(target=targets._reboot_target, daemon=True).start()
        detail = "재부팅이 승인되었습니다."
    
    return render_template("reboot.html", reboot_status=reboot_status, detail=detail)

@bp.route("/log", methods=["GET"])
@login_required
def log():
    return render_template("log.html", log=utils.get_log(), client_name=session.get('username'))