import threading
import config
from flask import Blueprint, flash, redirect, url_for
import modules.targets as targets
import modules.gpio_control as gpio_ctrl
from modules.logging import logger
from webservice.auth import login_required

bp = Blueprint('router', __name__, url_prefix='/alarm')

@bp.route("/turnon", methods=["GET"])
@login_required
def alarm_on():
    if config.get_config('alarm') == config.STATUS_ERROR:
        flash("경보기가 이미 작동 중입니다.")
        return redirect(url_for('home'))
    
    if config.get_config('alarm_poss') == False:
        flash("경보기 작동이 비활성화 되어있습니다.")
        return redirect(url_for('home'))
    
    threading.Thread(target=targets._alarm_turnon_target, daemon=True).start()
    flash("경보기를 작동했습니다.")
    return redirect("/")

@bp.route("/turnoff", methods=["GET"])
@login_required
def alarm_off():
    config.set_config('alarm', False)
    flash("경보기가 해제되었습니다.")
    
    return redirect("/")