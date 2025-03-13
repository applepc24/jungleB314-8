from datetime import timedelta
import os
from dotenv import load_dotenv

# 환경 변수 로드 (.env에서 불러오기)
load_dotenv()

# Flask 세션 및 flash에서 사용할 키 설정
SECRET_KEY = os.getenv('SECRET_KEY', 'your-flask-secret-key')

# JWT 설정
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-key-please-change-this')
JWT_TOKEN_LOCATION = ['cookies']
JWT_ACCESS_COOKIE_NAME = 'access_token'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
JWT_COOKIE_CSRF_PROTECT = False
