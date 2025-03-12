from flask import Blueprint, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId

board_bp = Blueprint('board', __name__, url_prefix='/board')

# Mongo 연결
from models.post_model import posts_collection

@board_bp.route('/<category>', methods=['GET'])
def board(category):
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    posts_per_page = 10

    query = {'category': category}

    if keyword:
        query['$or'] = [
            {'title': {'$regex': keyword, '$options': 'i'}},
            {'content': {'$regex': keyword, '$options': 'i'}}
        ]

    total_posts = posts_collection.count_documents(query)  # ✅ 전체 게시글 개수
    total_pages = (total_posts // posts_per_page) + (1 if total_posts % posts_per_page > 0 else 0)

    # ✅ 오래된 게시글이 1번이 되도록 오름차순 정렬
    posts = list(posts_collection.find(query)
             .sort('created_at', 1)  # 오름차순 정렬 (오래된 글이 먼저)
             .skip((page - 1) * posts_per_page)
             .limit(posts_per_page))

    # ✅ 인덱스를 전체 개수를 기준으로 역순으로 부여
    latest_index = total_posts - ((page - 1) * posts_per_page)  # 가장 최신 글 번호 계산
    for post in posts:
        post['_id'] = str(post['_id'])
        post['index'] = latest_index  # 가장 최신 글부터 역순으로 인덱스 부여
        latest_index -= 1  # 감소

    return render_template('board.html',
                           posts=posts,
                           category=category,
                           total_pages=total_pages,
                           current_page=page,
                           page_range=list(range(1, total_pages + 1)),
                           search_mode='category',
                           keyword=keyword)
