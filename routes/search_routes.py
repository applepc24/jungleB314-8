from flask import Blueprint, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId

search_bp = Blueprint('search', __name__)

# Mongo 연결
client = MongoClient('mongodb://localhost:27017')
db = client['jungle8_63']
posts_collection = db['posts']

@search_bp.route('/search', methods=['GET'])
def search_posts():
    keyword = request.args.get('keyword', '').strip()

    page = request.args.get('page', 1, type=int)
    posts_per_page = 10
    
    # 검색어가 없으면 메인으로 리다이렉트할 수도 있음
    if not keyword:
        return "검색어가 없습니다!", 400

    # 제목이나 내용에 키워드가 포함된 게시글 찾기 (대소문자 구분 없음)
    query = {
        "$or": [
            {"title": {"$regex": keyword, "$options": "i"}},
            {"content": {"$regex": keyword, "$options": "i"}}
        ]
    }
     # ✅ 전체 검색된 게시글 수
    total_posts = posts_collection.count_documents(query)

    # ✅ 전체 페이지 수 계산
    total_pages = (total_posts // posts_per_page) + (1 if total_posts % posts_per_page > 0 else 0)

    # ✅ 해당 페이지에 들어갈 게시글만 조회 (skip & limit)
    posts = list(posts_collection.find(query)
                 .sort('created_at', -1)
                 .skip((page - 1) * posts_per_page)
                 .limit(posts_per_page))

    # 게시글 번호 인덱스 달기
    for idx, post in enumerate(posts, start=1):
        post['_id'] = str(post['_id'])
        post['index'] = idx  # ✅ board.html에서 {{ post.index }} 쓰게 돼있음

    # ✅ 페이지 네비게이션에 넘길 페이지 리스트
    page_range = list(range(1, total_pages + 1))
    
    return render_template(
        'board.html',
        posts=posts,
        category=f"'{keyword}' 검색 결과입니다!",
        total_pages=total_pages,
        current_page=page,
        page_range=list(range(1, total_pages + 1)),
        search_mode='global'  # ✅ 템플릿에서 검색 여부 판단용
    )