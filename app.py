from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import timedelta
from routes import auth_bp, mypage_bp, main_bp, board_bp, post_bp, search_bp
from models.user_model import users_collection
from models.post_model import posts_collection 

from config import *

# 앱 생성
app = Flask(__name__)

# ✅ 설정값 적용 (config.py에서 불러오기)
app.config.from_object('config')

# ✅ JWT 설정 적용
jwt = JWTManager(app)

# ✅ CORS 설정 적용
CORS(app)

# ✅ Blueprint 등록
from routes import auth_bp, main_bp, mypage_bp, board_bp, post_bp
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(board_bp)
app.register_blueprint(post_bp)
app.register_blueprint(search_bp)

app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

# JWT 등록
jwt = JWTManager(app)
CORS(app)
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
