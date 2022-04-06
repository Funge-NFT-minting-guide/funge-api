SERVICE_URL = 'https://funge.kr'
DEVELOP_URL = 'http://localhost:8000'
SERVICE_HOST = '0.0.0.0'
SERVICE_PORT = 8000

TWITTY_URL = 'http://localhost:3000'
ADMIN_URL = 'http://localhost:9000'

SERVICE_ROOT = 'app'
UPLOAD_PATH = 'uploads'
UPLOAD_USERS = 'users'
ALLOWED_EXTENSIONS_IMAGES = set(['jpg', 'jpeg', 'png', 'bmp', 'gif'])

TOKEN_NEEDED = 101
TYPE_NOT_ALLOWED = 102
INVALID_TOKEN = 103
EXPIRED_TOKEN = 104

ERR_CODE_REQUIRED = (400, 'Code is required.')
ERR_USER_CANCELLED = (400, 'User candelled login.')
ERR_NOT_ALLOWED_TYPE = lambda x: (400, f'{x} type is not allowed.')
ERR_TOKEN_NEEDED = (400, 'Token is needed.')
ERR_TOKEN_INVALID = (400, 'Token is not valid.')
ERR_UNAUTHORIZED = (401, 'Unauthorized.')
ERR_TOKEN_EXPIRED = (412, 'Token has expired.')
ERR_NOT_EXPECTED = (400, 'Payload is not expected.')
ERR_NOT_FOUND = (404, 'No result found.')
