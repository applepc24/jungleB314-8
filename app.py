from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import * 

client = MongoClient('mongodb://localhost:27017')  # 또는 Atlas URI
db = client['jungle8_63']  # DB 이름
users_collection = db['users'] 

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_TOKEN_LOCATION'] = JWT_TOKEN_LOCATION
app.config['JWT_ACCESS_COOKIE_NAME'] = JWT_ACCESS_COOKIE_NAME
app.config['JWT_COOKIE_CSRF_PROTECT'] = JWT_COOKIE_CSRF_PROTECT

jwt = JWTManager(app)

# CORS 설정 추가
CORS(app)

# 루트에서 로그인 페이지로 리디렉션
@app.route('/')
def home():
    return redirect(url_for('login_page'))

# 로그인 페이지 렌더링 (GET)
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# 로그인 처리 (POST)
@app.route('/login', methods=['POST'])

def login():
    id = request.form.get('id')
    pw = request.form.get('pw')

    user = users_collection.find_one({'id': id})

    if not user:
        print("[로그인 실패] 사용자 없음")
        return render_template('login.html', error="아이디 또는 비밀번호가 틀렸습니다.")

    if user and user['pw'] == pw:
        user_id_str = str(user['_id'])
        token = create_access_token(identity=user_id_str, expires_delta=timedelta(minutes=30))

        response = make_response(redirect(url_for('main_page')))
        response.set_cookie('access_token', token, httponly=True, secure=False)

        return response

    return render_template('login.html', error="아이디 또는 비밀번호가 틀렸습니다.")
# 회원가입 페이지 렌더링 (GET)
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# 회원가입 처리 (POST)
@app.route('/signup', methods=['POST'])
def signup():
    id = request.form.get('id')
    pw = request.form.get('pw')
    pw_confirm = request.form.get('pw_confirm')
    nickname = request.form.get('nickname')

    print(f"[회원가입 요청] id: {id}, pw: {pw}, pw_confirm: {pw_confirm}, nickname: {nickname}")

    # 필수 입력값 검사
    if not id or not pw or not pw_confirm or not nickname:
        return jsonify({'msg': '모든 필드를 입력해야 합니다.'}), 400
    
    if pw != pw_confirm:
        return jsonify({'msg': '비밀번호가 일치하지 않습니다.'}), 400
    
    # ✅ ID 중복 검사 (MongoDB에서 검사)
    existing_user = users_collection.find_one({'id': id})

    if existing_user:
        return jsonify({'msg': '이미 존재하는 사용자입니다.'}), 400
    
    # 사용자 저장
    try:
        result = users_collection.insert_one({
            'id': id,
            'pw': pw,
            'nickname': nickname
        })
        print(f"[회원가입 성공] inserted_id: {result.inserted_id}")

        return jsonify({'msg': '회원가입 성공!'})
    
    except Exception as e:
        print(f"[회원가입 실패] DB 오류: {e}")
        return jsonify({'msg': '서버 오류 발생'}), 500

# 메인 페이지 라우팅 (JWT 필요)
@app.route('/main', methods=['GET'])
@jwt_required(locations=["cookies"])
def main_page():
    user_id = get_jwt_identity()

    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        return redirect(url_for('login_page'))

    nickname = user['nickname']
    return render_template('main.html', user=user['id'], nickname=nickname)

# ✅ 로그아웃 (쿠키에서 JWT 삭제)
@app.route('/logout', methods=['GET'])
def logout():
    response = make_response(redirect(url_for('login_page')))
    response.delete_cookie('access_token', path='/')  # 경로 명시적으로 삭제
    return response

# 게시판 라우팅 (JWT 필요)
@app.route('/board/<category>', methods=['GET'])
@jwt_required()
def board(category):
    return f"{category} 게시판 페이지"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
