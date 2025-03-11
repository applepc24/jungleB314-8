from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from models.user_model import users_collection

main_bp = Blueprint('main', __name__)

@main_bp.route('/main', methods=['GET'])
@jwt_required(locations=["cookies"])
def main_page():
    user_id = get_jwt_identity()

    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        return redirect(url_for('auth.login_page'))

    nickname = user['nickname']
    return render_template('main.html', user=user['id'], nickname=nickname)

@main_bp.route('/board/<category>', methods=['GET'])
@jwt_required(locations=["cookies"])
def board(category):
    return f"{category} 게시판 페이지"