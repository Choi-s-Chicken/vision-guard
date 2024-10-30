import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# User db path
USER_DB_PATH = f'{BASE_DIR}/db/users.json'
def get_user_db():
    with open(USER_DB_PATH, 'r') as f:
        return json.load(f)

# Products db path
PRODUCTS_DB_PATH = f'{BASE_DIR}/db/products.json'
def get_products_db():
    with open(PRODUCTS_DB_PATH, 'r') as f:
        return json.load(f)


# model path
FACE_DECT_MODEL_PATH = f'{BASE_DIR}/src/models/face-detection-adas-0001'
FACE_REID_MODEL_PATH = f'{BASE_DIR}/src/models/face-reidentification-retail-0095'

