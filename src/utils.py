import hashlib
import os
import time


def get_now_ftime(format="%Y%m%d_%H%M%S"):
    return time.strftime(format, time.localtime())

def convert_str_to_time(str_time, format="%Y%m%d_%H%M%S"):
    return time.strptime(str_time, format)

def gen_rhash(length=64):
    random_bytes = os.urandom(32)
    hash_object = hashlib.sha256(random_bytes)
    random_hash = hash_object.hexdigest()
    return random_hash[:length]

def get_file_ext(file_name):
    if '.' not in file_name:
        return None
    return file_name.split('.')[-1] 