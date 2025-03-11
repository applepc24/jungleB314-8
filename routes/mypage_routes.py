from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from models.user_model import users_collection
from models.post_model import posts_collection  # 게시글 DB 연결 필요!

mypage_bp = Blueprint('mypage', __name__)

# 마이페이지 조회
@mypage_bp.route('/mypage', methods=['GET'])
@jwt_required(locations=["cookies"])
def mypage():
    user_id = get_jwt_identity()

    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return redirect(url_for('auth.login_page'))

    posts = posts_collection.find({"author_id": user_id})

    posts_list = [{"title": post["title"], "content": post["content"]} for post in posts]

    return render_template('mypage.html', user=user, posts=posts_list)

# 마이페이지 프로필 수정
@mypage_bp.route('/mypage/update', methods=['POST'])
@jwt_required(locations=["cookies"])
def update_profile():
    user_id = get_jwt_identity()

    new_nickname = request.form.get('nickname')
    new_password = request.form.get('password')

    update_data = {}

    if new_nickname:
        update_data["nickname"] = new_nickname

    if new_password:
        update_data["pw"] = new_password  # ❗ 비밀번호 해싱을 고려해야 함!

    if update_data:
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    return jsonify({'msg': '프로필이 성공적으로 수정되었습니다.'})