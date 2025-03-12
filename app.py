from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import timedelta

client = MongoClient('mongodb://localhost:27017')  # 또는 Atlas URI
db = client['jungle8_63']  # DB 이름
users_collection = db['users']
posts_collection = db['posts']  # ✅ 게시글 저장하는 컬렉션 추가
from config import *

# 블루프린트 등록
from routes import auth_bp, main_bp, mypage_bp, board_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(board_bp)

# 앱 생성
app = Flask(__name__)


app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False



# DB 연결
client = MongoClient('mongodb://localhost:27017')
db = client['jungle8_63']

# JWT 등록
jwt = JWTManager(app)

<<<<<<< HEAD
CORS(app)

@app.route('/')
def home():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    id = request.form.get('id')
    pw = request.form.get('pw')

    user = users_collection.find_one({'id': id})

    if not user or user['pw'] != pw:
        print("[로그인 실패] 사용자 없음 또는 비밀번호 불일치")
        response = make_response(render_template('login.html', error="아이디 또는 비밀번호가 틀렸습니다."))
        response.delete_cookie('access_token', path="/")
        return response

    user_id_str = str(user['_id'])
    token = create_access_token(identity=user_id_str, expires_delta=timedelta(minutes=30))

    response = make_response(redirect(url_for('main_page')))
    response.set_cookie('access_token', token, httponly=True, secure=False, path="/")
    return response

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    id = request.form.get('id')
    pw = request.form.get('pw')
    pw_confirm = request.form.get('pw_confirm')
    nickname = request.form.get('nickname')

    print(f"[회원가입 요청] id: {id}, pw: {pw}, pw_confirm: {pw_confirm}, nickname: {nickname}")

    if not id or not pw or not pw_confirm or not nickname:
        return jsonify({'msg': '모든 필드를 입력해야 합니다.'}), 400
    
    if pw != pw_confirm:
        return jsonify({'msg': '비밀번호가 일치하지 않습니다.'}), 400
    
    existing_user = users_collection.find_one({'id': id})

    if existing_user:
        return jsonify({'msg': '이미 존재하는 사용자입니다.'}), 400
    
    try:
        result = users_collection.insert_one({'id': id, 'pw': pw, 'nickname': nickname})
        print(f"[회원가입 성공] inserted_id: {result.inserted_id}")
        return jsonify({'msg': '회원가입 성공!'})
    
    except Exception as e:
        print(f"[회원가입 실패] DB 오류: {e}")
        return jsonify({'msg': '서버 오류 발생'}), 500

@app.route('/main', methods=['GET'])
@jwt_required(locations=["cookies"])
def main_page():
    user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        return redirect(url_for('login_page'))

    nickname = user['nickname']
    return render_template('main.html', user=user['id'], nickname=nickname)

# 마이페이지 구현 (닉네임 & 비밀번호 수정 + 내가 쓴 글 목록)
@app.route('/mypage', methods=['GET'])
@jwt_required(locations=["cookies"])
def mypage():
    user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        return redirect(url_for('login_page'))

    posts = posts_collection.find({"author_id": user_id})
    posts_list = [
            {"title": post["title"], "content": post["content"], "category": post["category"], "_id": str(post["_id"])}
            for post in posts
        ]
    return render_template('mypage.html', user=user, posts=posts_list)

#개인정보수정
@app.route('/mypage/update', methods=['POST'])
@jwt_required(locations=["cookies"])
def update_profile():
    user_id = get_jwt_identity()
    new_nickname = request.form.get('nickname')
    new_password = request.form.get('password')

    update_data = {}

    if new_nickname:
        update_data["nickname"] = new_nickname

    if new_password:
        update_data["pw"] = new_password  # ✅ 해싱 없이 비밀번호 저장

    if update_data:
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    return jsonify({'msg': '프로필이 성공적으로 수정되었습니다.'})

#게시판
@app.route('/board/<category>', methods=['GET'])
def board(category):
    page = request.args.get('page', 1, type=int)  # 현재 페이지 번호
    posts_per_page = 10  # 페이지당 표시할 게시글 개수

    total_posts = posts_collection.count_documents({'category': category})  # 전체 게시글 개수
    total_pages = (total_posts // posts_per_page) + (1 if total_posts % posts_per_page > 0 else 0)

    posts = list(posts_collection.find({'category': category})
                 .sort('created_at', -1)
                 .skip((page - 1) * posts_per_page)
                 .limit(posts_per_page))

    for idx, post in enumerate(posts, start=(page - 1) * posts_per_page + 1):  # 인덱스 번호 추가
        post['_id'] = str(post['_id'])
        post['index'] = idx

    # ✅ Jinja에서 range()를 사용할 수 없으므로 리스트로 변환하여 넘겨줌
    page_range = list(range(1, total_pages + 1))

    return render_template('board.html', posts=posts, category=category, total_pages=total_pages, 
                           current_page=page, page_range=page_range)


#글쓰기 페이지 렌더링
@app.route('/board/<category>/write', methods=['GET'])
@jwt_required(locations=["cookies"])
def write_page(category):
    return render_template('write.html', category=category)

#글쓰기
@app.route('/board/<category>/write', methods=['POST'])
@jwt_required(locations=["cookies"])
def write_post(category):
    user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        return redirect(url_for('login_page'))

    title = request.form.get('title')
    content = request.form.get('content')
    is_anonymous = 'is_anonymous' in request.form  # 체크박스 선택 여부 확인
    nickname = "익명" if is_anonymous else user['nickname']  # 익명 여부에 따라 닉네임 설정

    new_post = {
        'title': title,
        'content': content,
        'author_id': user_id,
        'nickname': nickname,  # 익명 여부 반영
        'category': category,
    }

    posts_collection.insert_one(new_post)

    return redirect(url_for('board', category=category))

@app.route('/board/<category>/post/<post_id>')
def post_detail(category, post_id):
    post = posts_collection.find_one({'_id': ObjectId(post_id)})

    if not post:
        return "게시글을 찾을 수 없습니다.", 404

    return render_template('post.html', post=post, category=category)

# 로그아웃
@app.route('/logout', methods=['GET'])
def logout():
    response = make_response(redirect(url_for('login_page')))
    response.delete_cookie('access_token', path="/")
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)