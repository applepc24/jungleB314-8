from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson.objectid import ObjectId

# 블루프린트 만들기
board_bp = Blueprint('board', __name__, url_prefix='/board')

# Mongo 연결 (네 설정에 맞게)
client = MongoClient('mongodb://localhost:27017')
db = client['jungle8_63']
posts_collection = db['posts']

@board_bp.route('/board/<category>', methods=['GET'])
@jwt_required(locations=["cookies"])
def board(category):
    # 쿼리 파라미터에서 page 번호 받아오기 (기본값 1)
    page = int(request.args.get('page', 1))
    per_page = 10
    skip = (page - 1) * per_page

    # ✅ DB에서 카테고리에 해당하는 게시글 찾기
    posts_cursor = posts_collection.find({'category': category}).skip(skip).limit(per_page)

    posts = []
    index = skip + 1
    for post in posts_cursor:
        posts.append({
            'order': index,
            'category': post.get('category', ''),
            'nickname': post.get('nickname', ''),
            'title': post.get('title', ''),
            'content': post.get('content', '')
        })
        index += 1

    # ✅ 페이지 수 계산
    total_posts = posts_collection.count_documents({'category': category})
    total_pages = (total_posts + per_page - 1) // per_page

    # ✅ board.html 템플릿으로 데이터 넘기기
    return render_template('board_list.html', category=category, posts=post_list, total_pages=total_pages)