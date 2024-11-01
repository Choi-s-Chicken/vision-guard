from datetime import datetime
import hashlib
import os
import subprocess

import config

log_time_format = "%Z %x %X"
log_format = "%(asctime)s %(levelname)8s %(message)s"
default_timef = "%Y%m%d%H%M%S"

def get_log() -> str:
    with open(config.LOG_PATH, 'r', encoding='utf-8') as f:
        return f.read()
def init_log():
    with open(config.LOG_PATH, 'w', encoding='utf-8') as f:
        f.write("")

def get_now_ftime(time_format: str | None = default_timef) -> str:
    time = datetime.now()
    f_time = time.strftime(time_format)
    return f_time

def get_now_iso_time() -> str:
    time = datetime.now()
    return time.isoformat()

def convert_now_ftime(_time_str: str, _format = '%Y%m%d%H%M%S') -> datetime:
    return datetime.strptime(_time_str, _format)

def get_local_ip(_defalut:str = "N/A") -> str:
    try:
        ip = subprocess.check_output(['hostname', '-I']).decode('utf-8').strip()
        ip_address = ip if ip else _defalut
    except Exception:
        ip_address = _defalut
    return ip_address

def get_client_ip(request) -> str:
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

def gen_hash(data: str | None = str(os.urandom(16))) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()