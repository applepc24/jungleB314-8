from flask import Blueprint, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId

board_bp = Blueprint('board', __name__, url_prefix='/board')

# Mongo 연결 (다른 곳에서 클라이언트 만들어서 넘길 수도 있음)
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

    total_posts = posts_collection.count_documents(query)
    total_pages = (total_posts // posts_per_page) + (1 if total_posts % posts_per_page > 0 else 0)

    posts = list(posts_collection.find(query)
             .sort('created_at', -1)
             .skip((page - 1) * posts_per_page)
             .limit(posts_per_page))

    for idx, post in enumerate(posts, start=(page - 1) * posts_per_page + 1):
        post['_id'] = str(post['_id'])
        post['index'] = idx

    page_range = list(range(1, total_pages + 1))

    return render_template('board.html',
                           posts=posts,
                           category=category,
                           total_pages=total_pages,
                           current_page=page,
                           page_range=list(range(1, total_pages + 1)),
                           search_mode='category',  # ✅ 검색 여부 전달
                           keyword=keyword)