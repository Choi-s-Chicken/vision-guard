from datetime import datetime
import random
import time
import os
import hashlib
import cv2
import numpy as np
from openvino.runtime import Core
import config

default_timef = "%Y%m%d%H%M%S"

def get_now_iso_ftime() -> str:
    now = datetime.now()
    return now.isoformat()

def get_now_ftime(_format = config.DF_TIME_FORMAT) -> str:
    now = datetime.now()
    return now.strftime(_format)

def convert_now_ftime(_time_str: str, _format = config.DF_TIME_FORMAT) -> datetime:
    return datetime.strptime(_time_str, _format)

def convert_str_to_time(_str_time, _format=default_timef):
    return datetime.strptime(_str_time, _format)

def re_time_string_format(_str_time, _reformat, _format=default_timef) -> str:
    return convert_str_to_time(_str_time, _format).strftime(_reformat)

def gen_rhash(length=64):
    random_bytes = os.urandom(32)
    hash_object = hashlib.sha256(random_bytes)
    random_hash = hash_object.hexdigest()
    return random_hash[:length]

def gen_hash(_data: str | None = str(random.randbytes), _salt="797882ad4a5fe5be") -> str:
    return hashlib.sha256(f"{_data}+{_salt}".encode('utf-8')).hexdigest()

def get_file_ext(file_name):
    if '.' not in file_name:
        return None
    return file_name.split('.')[-1] 




