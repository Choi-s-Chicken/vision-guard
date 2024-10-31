import os
import json

# Init
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = f'{BASE_PATH}/db'
DF_TIME_FORMAT = '%Y%m%d%H%M%S'

# User db path
USER_DB_PATH = f'{DB_PATH}/users.json'
def get_user_db(_default=[]):
    try:
        with open(USER_DB_PATH, 'r') as f:
            return json.load(f)
    except:
        return _default
def set_user_db(_data):
    with open(USER_DB_PATH, 'w') as f:
        json.dump(_data, f)
USER_ID_RE = r'^[A-Za-z0-9]{2,16}$'
USER_PW_RE = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+~`|}{[\]:;?><,./\-]).{8,256}$'
USER_NM_RE = r'^[가-힣]{1,8}$'

# Space db path
SPACE_DB_PATH = f'{DB_PATH}/spaces.json'
SPACE_NM_RE = r'^[가-힣a-zA-Z0-9]{2,16}$$'

# Products db path
PRODUCTS_DB_PATH = f'{DB_PATH}/products.json'
def get_products_db(_default=[]):
    try:
        with open(PRODUCTS_DB_PATH, 'r') as f:
            return json.load(f)
    except:
        return _default
def set_products_db(_data):
    with open(PRODUCTS_DB_PATH, 'w') as f:
        json.dump(_data, f)

# model path
FACE_DECT_MODEL_PATH = f'{BASE_PATH}/src/models/face-detection-adas-0001'
FACE_REID_MODEL_PATH = f'{BASE_PATH}/src/models/face-reidentification-retail-0095'

