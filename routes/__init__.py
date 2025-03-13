from .auth_routes import auth_bp
from .main_routes import main_bp
from .mypage_routes import mypage_bp
from .board_routes import board_bp
from .post_routes import post_bp
from .search_routes import search_bp

__all__ = ['auth_bp', 'main_bp', 'board_bp', 'mypage_bp', 'post_bp', 'search_bp']
