from datetime import timedelta

JWT_SECRET_KEY = 'super-secret-key-please-change-this'
JWT_TOKEN_LOCATION = ['cookies']
JWT_ACCESS_COOKIE_NAME = 'access_token'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
JWT_COOKIE_CSRF_PROTECT = False