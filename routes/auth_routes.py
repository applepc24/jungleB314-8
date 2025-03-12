from flask import Blueprint, render_template, request, jsonify, redirect, url_for, make_response
from flask_jwt_extended import create_access_token
from datetime import timedelta
from bson.objectid import ObjectId
from pymongo import MongoClient

from models.user_model import users_collection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login_page'))

# 로그인 페이지
@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# 로그인 처리
@auth_bp.route('/login', methods=['POST'])
def login():
    id = request.form.get('id')
    pw = request.form.get('pw')

    user = users_collection.find_one({'id': id})

    if not user or user['pw'] != pw:
        print("[로그인 실패] 사용자 없음 또는 비밀번호 오류")
        return render_template('login.html', error="아이디 또는 비밀번호가 틀렸습니다.")

    user_id_str = str(user['_id'])
    token = create_access_token(identity=user_id_str, expires_delta=timedelta(minutes=30))

    response = make_response(redirect(url_for('main.main_page')))
    response.set_cookie('access_token', token, httponly=True, secure=False)
    return response

# 회원가입 페이지
@auth_bp.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# 회원가입 처리
@auth_bp.route('/signup', methods=['POST'])
def signup():
    id = request.form.get('id')
    pw = request.form.get('pw')
    pw_confirm = request.form.get('pw_confirm')
    nickname = request.form.get('nickname')

    if not id or not pw or not pw_confirm or not nickname:
        return jsonify({'msg': '모든 필드를 입력해야 합니다.'}), 400

    if pw != pw_confirm:
        return jsonify({'msg': '비밀번호가 일치하지 않습니다.'}), 400

    existing_user = users_collection.find_one({'id': id})
    if existing_user:
        return jsonify({'msg': '이미 존재하는 사용자입니다.'}), 400

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

# 로그아웃 처리
@auth_bp.route('/logout', methods=['GET'])
def logout():
    response = make_response(redirect(url_for('auth.login_page')))
    response.delete_cookie('access_token', path='/')
    return response