from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime

from models.user_model import users_collection
from models.post_model import posts_collection

post_bp = Blueprint('post', __name__)

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
        'index': new_index,
        'views' : 0,
        'likes' : 0,
        'created_at': datetime.utcnow()
    }
    posts_collection.insert_one(new_post)

    return redirect(url_for('board.board', category=category))

# 게시글 상세보기
@post_bp.route('/board/<category>/post/<post_id>')
@jwt_required(locations=["cookies"])
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

@post_bp.route('/board/<category>/post/<post_id>/like', methods=['POST'])
@jwt_required(locations=["cookies"])
def like_post(category, post_id):
    user_id = get_jwt_identity()

    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        return jsonify({'msg': '게시글을 찾을 수 없습니다.'}), 404
    
    # 좋아요 수 증가
    posts_collection.update_one(
        {'_id': ObjectId(post_id)},
        {'$inc': {'likes': 1}}
    )

    return jsonify({'msg': '좋아요가 반영되었습니다!'})

@post_bp.route('/board/<category>/post/<post_id>/comment', methods=['POST'])
@jwt_required(locations=["cookies"])
def add_comment(category, post_id):
    user_id = get_jwt_identity()
    content = request.form.get('content')
    is_anonymous = request.form.get('is_anonymous') == 'true'

    if not content:
        return jsonify({'msg': '댓글 내용을 입력해주세요.'}), 400

    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'msg': '사용자를 찾을 수 없습니다.'}), 404

    nickname = "익명" if is_anonymous else user.get('nickname')

    # ✅ 댓글에 명확히 '_id'를 추가
    new_comment = {
        '_id': ObjectId(),  # ✅ 명확하게 ObjectId로 설정
        'content': content,
        'nickname': nickname,
        'user_id': user_id,
        'created_at': datetime.utcnow()
    }

    # ✅ 댓글 추가
    posts_collection.update_one(
        {'_id': ObjectId(post_id)},
        {'$push': {'comments': new_comment}}
    )

    return jsonify({'msg': '댓글이 추가되었습니다.'})


@post_bp.route('/board/<category>/post/<post_id>/comment/<comment_id>/delete', methods=['POST'])
@jwt_required(locations=["cookies"])
def delete_comment(category, post_id, comment_id):
    user_id = get_jwt_identity()

    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        return jsonify({'msg': '게시글을 찾을 수 없습니다.'}), 404

    try:
        comment_id = ObjectId(comment_id)
    except:
        return jsonify({'msg': '잘못된 댓글 ID입니다.'}), 400

    # ✅ 댓글 가져오기 (get()으로 KeyError 방지)
    comments = post.get('comments', [])

    # ✅ 댓글 삭제 (ID와 작성자 ID가 일치할 경우만 삭제)
    updated_comments = [
        c for c in comments 
        if c.get('_id') != comment_id or c.get('user_id') != user_id
    ]

    # ✅ 변경된 댓글 리스트로 업데이트
    posts_collection.update_one(
        {'_id': ObjectId(post_id)},
        {'$set': {'comments': updated_comments}}
    )

    return jsonify({'msg': '댓글이 삭제되었습니다.'})
