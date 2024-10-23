import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv(verbose=True)
HOST_IP = os.getenv('HOST_IP')
HOST_PORT = os.getenv('HOST_PORT')

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=True, host=HOST_IP, port=HOST_PORT)