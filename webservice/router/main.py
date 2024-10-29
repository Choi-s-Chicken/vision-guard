from flask import Blueprint

import webservice.router.alarm.main as alarm
import webservice.router.system.main as system

bp = Blueprint('router', __name__)

bp.register_blueprint(alarm.bp)
bp.register_blueprint(system.bp)