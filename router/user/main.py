from flask import Blueprint, request, jsonify

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'User index!'})