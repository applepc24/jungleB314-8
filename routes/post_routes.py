from flask import Blueprint, render_template, request, redirect, url_for, flash, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from pymongo import MongoClient

post_bp = Blueprint('post', __name__)

from models.user_model import users_collection
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
        flash("사용자 정보를 찾을 수 없습니다.")
        return redirect(url_for('auth.login_page'))

    title = request.form.get('title')
    content = request.form.get('content')
    is_anonymous = request.form.get('is_anonymous') == 'on'
    nickname = "익명" if is_anonymous else user.get('nickname')

    if not title or not content:
        flash("제목과 내용을 입력해주세요.")
        return redirect(url_for('post.write_page', category=category))

    # 최신 글의 index 값을 가져와서 1 증가
    last_post = posts_collection.find_one({'category': category}, sort=[("index", -1)])
    new_index = (last_post.get("index", 0) + 1) if last_post else 1

    new_post = {
        'title': title,
        'content': content,
        'author_id': user_id,
        'nickname': nickname,
        'category': category,
        'index': new_index
    }

    # MongoDB에 삽입 및 성공 여부 체크
    result = posts_collection.insert_one(new_post)
    if not result.inserted_id:
        flash("게시글 저장에 실패했습니다.")
        return redirect(url_for('board.board', category=category))

    flash("게시글이 성공적으로 작성되었습니다.")
    return redirect(url_for('board.board', category=category))

   # ✅ 게시글 상세보기 라우트
@post_bp.route('/board/<category>/post/<post_id>', methods=['GET'])
def post_detail(category, post_id):
    user_id = get_jwt_identity()
    post = posts_collection.find_one({'_id': ObjectId(post_id)})

    if not post:
        flash("게시글을 찾을 수 없습니다.")
        return redirect(url_for('board.board', category=category))

    return render_template('post.html', post=post, category=category, user_id=user_id)

# 글 삭제
@post_bp.route('/board/<category>/post/<post_id>/delete', methods=['POST'])
@jwt_required(locations=["cookies"])
def delete_post(category, post_id):
    user_id = get_jwt_identity()
    post = posts_collection.find_one({'_id': ObjectId(post_id)})

    if not post:
        flash("게시글이 존재하지 않습니다.")
        return redirect(url_for('board.board', category=category))

    if post['author_id'] != user_id:
        flash("삭제할 권한이 없습니다.")
        return redirect(url_for('post.post_detail', category=category, post_id=post_id))

    result = posts_collection.delete_one({'_id': ObjectId(post_id)})
    if result.deleted_count == 0:
        flash("게시글 삭제에 실패했습니다.")
        return redirect(url_for('post.post_detail', category=category, post_id=post_id))

    flash("게시글이 성공적으로 삭제되었습니다.")
    return redirect(url_for('board.board', category=category))

# 글 수정
@post_bp.route('/board/<category>/post/<post_id>/edit', methods=['GET', 'POST'])
@jwt_required(locations=["cookies"])
def edit_post(category, post_id):
    user_id = get_jwt_identity()
    post = posts_collection.find_one({'_id': ObjectId(post_id)})

    if not post:
        flash("게시글을 찾을 수 없습니다.")
        return redirect(url_for('board.board', category=category))
    
    if post['author_id'] != user_id:
        flash("수정할 권한이 없습니다.")
        return redirect(url_for('post.post_detail', category=category, post_id=post_id))

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_content = request.form.get('content')

        if not new_title or not new_content:
            flash("제목과 내용을 입력해주세요.")
            return redirect(url_for('post.edit_post', category=category, post_id=post_id))

        result = posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': {'title': new_title, 'content': new_content}}
        )

        if result.modified_count == 0:
            flash("게시글 수정에 실패했습니다.")
        else:
            flash("게시글이 수정되었습니다.")

        return redirect(url_for('post.post_detail', category=category, post_id=post_id))

    return render_template('edit_post.html', post=post, category=category)



@post_bp.route('/board/<category>/post/<post_id>/comment', methods=['POST'])
@jwt_required(locations=["cookies"])
def add_comment(category, post_id):
    user_id = get_jwt_identity()
    post = posts_collection.find_one({'_id': ObjectId(post_id)})

    if not post:
        return jsonify({'msg': '게시글이 존재하지 않습니다.'}), 404

    content = request.form.get('content')
    
    # 'true' 또는 'false' 문자열을 Boolean 값으로 변환
    is_anonymous = request.form.get('is_anonymous') == 'true'

    if not content:
        return jsonify({'msg': '댓글 내용을 입력해주세요.'}), 400

    # 익명이면 닉네임 대신 '익명' 저장
    user = posts_collection.find_one({'author_id': user_id})
    nickname = "익명" if is_anonymous else user['nickname']

    new_comment = {
        "_id": ObjectId(),
        "user_id": user_id,
        "nickname": nickname,
        "content": content
    }

    posts_collection.update_one(
        {'_id': ObjectId(post_id)},
        {'$push': {'comments': new_comment}}
    )

    return jsonify({'msg': '댓글이 작성되었습니다.'}), 201


# 댓글 삭제 API 수정
@post_bp.route('/board/<category>/post/<post_id>/comment/<comment_id>/delete', methods=['POST'])
@jwt_required(locations=["cookies"])
def delete_comment(category, post_id, comment_id):
    user_id = get_jwt_identity()

    post = posts_collection.find_one({'_id': ObjectId(post_id)})

    if not post:
        return jsonify({'msg': '게시글이 존재하지 않습니다.'}), 404

    # comment_id를 ObjectId로 변환해서 매칭
    try:
        comment_object_id = ObjectId(comment_id)
    except Exception:
        return jsonify({'msg': '잘못된 댓글 ID입니다.'}), 400

    comment = next((c for c in post['comments'] if c['_id'] == comment_object_id), None)
    
    if not comment:
        return jsonify({'msg': '댓글이 존재하지 않습니다.'}), 404

    if comment['user_id'] != user_id:
        return jsonify({'msg': '댓글 삭제 권한이 없습니다.'}), 403

    # 댓글 삭제 (ObjectId로 매칭 처리)
    result = posts_collection.update_one(
        {'_id': ObjectId(post_id)},
        {'$pull': {'comments': {'_id': comment_object_id}}}
    )

    if result.modified_count == 0:
        return jsonify({'msg': '댓글 삭제에 실패했습니다.'}), 500

    return jsonify({'msg': '댓글이 삭제되었습니다.'}), 200
