from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')  # 네가 쓰는 URI로 수정!
db = client['jungle8_63']  # 네가 쓰는 DB 이름으로 수정!
posts_collection = db['posts']  # 컬렉션 이름 확인!

# created_at 없는 글 찾기
posts = posts_collection.find({'created_at': {'$exists': False}})

for post in posts:
    post_id = post['_id']
    # ObjectId에서 생성 시간 가져오기
    created_at = post_id.generation_time  # datetime 반환됨

    # created_at 필드 추가
    posts_collection.update_one(
        {'_id': post_id},
        {'$set': {'created_at': created_at}}
    )

    print(f"Updated post {post_id} with created_at {created_at}")

print("모든 게시글에 created_at 필드를 추가했습니다!")