from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from config import *  # ✅ 설정값 불러오기

# ✅ MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client['jungle8_63']
users_collection = db['users']
posts_collection = db['posts']

# ✅ Flask 앱 생성
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

# ✅ 앱 실행 설정
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
