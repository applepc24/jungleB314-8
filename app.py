from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # JWT 시크릿 키 설정
jwt = JWTManager(app)

# CORS 설정 추가
CORS(app)

# 테스트 사용자
users = {
    '123': {
        'pw': '123',
        'nickname': 'test'
    }
}

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

    if id in users and users[id]['pw'] == pw:
        token = create_access_token(identity=id)  # JWT 토큰 생성
        print(token);
        return jsonify(access_token=token)  # 토큰 반환
    else:
        return jsonify({'msg': '로그인 실패'}), 401

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

    # 필수 입력값 검사
    if not id or not pw or not pw_confirm or not nickname:
        return jsonify({'msg': '모든 필드를 입력해야 합니다.'}), 400
    
    # ID 중복 검사
    if id in users:
        return jsonify({'msg': '이미 존재하는 사용자입니다.'}), 400
    
    # 비밀번호 일치 검사
    if pw != pw_confirm:
        return jsonify({'msg': '비밀번호가 일치하지 않습니다.'}), 400
    
    # 사용자 저장
    users[id] = {'pw': pw, 'nickname': nickname}
    return jsonify({'msg': '회원가입 성공!'})

# 대시보드 렌더링 (JWT 필요)
@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    token = request.headers.get('Authorization')
    print(f"Authorization 헤더 값: {token}")  # 디버깅용 출력 추가

    current_user = get_jwt_identity()
    nickname = users.get(current_user, {}).get('nickname', '알 수 없음')
    return render_template('dashboard.html', user=current_user, nickname=nickname)

# 메인 페이지 라우팅 (JWT 필요)
@app.route('/main', methods=['GET'])
@jwt_required()
def main_page():
    token = request.headers.get('Authorization')
    print(f"Authorization 헤더 값: {token}")  # 디버깅용 출력 추가
    
    current_user = get_jwt_identity()
    nickname = users.get(current_user, {}).get('nickname', '알 수 없음')
    return render_template('main.html', user=current_user, nickname=nickname)

# 로그아웃 라우팅
@app.route('/logout', methods=['GET'])
def logout():
    return redirect(url_for('login_page'))

# 게시판 라우팅 (JWT 필요)
@app.route('/board/<category>', methods=['GET'])
@jwt_required()
def board(category):
    return f"{category} 게시판 페이지"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
