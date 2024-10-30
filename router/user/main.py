from flask import Blueprint, render_template, request, jsonify
from modules.auth import 

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/login', methods=['GET'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        userpw = request.form['userpw']
        
        if 
    
    return render_template('user/login.html')
