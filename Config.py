# .env ファイルをロードして環境変数へ反映
from dotenv import load_dotenv
import os

JSON_AS_ASCII = False

COOKIE_DOMAIN = ''
COOKIE_SECURE = False
COOKIE_HTTPONLY = True

COOKIE_MAXAGE_DAYS = 1
COOKIE_NEXT_MAXAGE = 1

STATIC_BPNAME = 'Static'

LINE_BPNAME = 'Line'

LIFF_BPNAME = 'Liff'

#アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['jpeg','jpg','png','gif','bmp','svg','ico'])

load_dotenv('./.env', encoding='utf-8')
debug = os.environ['DEBUG'] == 'TRUE'
