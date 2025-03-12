
from flask import Blueprint, render_template, request, redirect, url_for, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from models.user_model import users_collection
from pymongo import MongoClient

post_bp = Blueprint('post', __name__)

from models.post_model import posts_collection 

# 글쓰기 페이지 렌더링
@post_bp.route('/board/<category>/write', methods=['GET'])
@jwt_required(locations=["cookies"])
def write_page(category):
    return render_template('write.html', category=category)

# 글쓰기 등록
@post_bp.route('/board/<category>/write', methods=['POST'])
@jwt_required(locations=["cookies"])
def write_post(category):
    user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        return redirect(url_for('auth.login_page'))

    title = request.form.get('title')
    content = request.form.get('content')
    is_anonymous = 'is_anonymous' in request.form
    nickname = "익명" if is_anonymous else user['nickname']

    new_post = {
        'title': title,
        'content': content,
        'author_id': user_id,
        'nickname': nickname,
        'category': category,
    }

    posts_collection.insert_one(new_post)

    return redirect(url_for('board.board', category=category))

   # ✅ 게시글 상세보기 라우트
@post_bp.route('/board/<category>/post/<post_id>', methods=['GET'])
def post_detail(category, post_id):
    post = posts_collection.find_one({'_id': ObjectId(post_id)})

    if not post:
        return "게시글을 찾을 수 없습니다.", 404

    return render_template('post.html', post=post, category=category)