from flask import Flask
from flask_jwt_extended import JWTManager, jwt_required
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import timedelta
from routes import auth_bp,mypage_bp,main_bp,board_bp,post_bp
#  main_bp, 
# mypage_bp
client = MongoClient('mongodb://localhost:27017')  # 또는 Atlas URI
db = client['jungle8_63']  # DB 이름
users_collection = db['users']
posts_collection = db['posts']  # ✅ 게시글 저장하는 컬렉션 추가
from config import *

# 앱 생성
app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(board_bp)
app.register_blueprint(post_bp)

app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

# DB 연결
client = MongoClient('mongodb://localhost:27017')
db = client['jungle8_63']

# JWT 등록
jwt = JWTManager(app)
CORS(app)
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)