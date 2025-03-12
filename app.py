from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from config import *

# 앱 생성
app = Flask(__name__)

# 앱 설정
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_TOKEN_LOCATION'] = JWT_TOKEN_LOCATION
app.config['JWT_ACCESS_COOKIE_NAME'] = JWT_ACCESS_COOKIE_NAME
app.config['JWT_COOKIE_CSRF_PROTECT'] = JWT_COOKIE_CSRF_PROTECT

# DB 연결
client = MongoClient('mongodb://localhost:27017')
db = client['jungle8_63']

# JWT 등록
jwt = JWTManager(app)

# CORS 등록
CORS(app)

# 블루프린트 등록
from routes import auth_bp, main_bp, mypage_bp, board_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(board_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)