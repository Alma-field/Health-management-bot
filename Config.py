# .env ファイルをロードして環境変数へ反映
from dotenv import load_dotenv

JSON_AS_ASCII = False

COOKIE_DOMAIN = ''
COOKIE_SECURE = False
COOKIE_HTTPONLY = True

COOKIE_MAXAGE_DAYS = 1
COOKIE_NEXT_MAXAGE = 1

STATIC_BPNAME = 'Static'

USER_BPNAME = 'User'
LOGIN_FUNCTION = f'{USER_BPNAME}.Login'
HOME_FUNCTION = f'{USER_BPNAME}.PossessionDenList'

API_BPNAME = 'Api'

LINE_BPNAME = 'Line'

LIFF_BPNAME = 'Liff'

ADMIN_BPNAME = 'Admin'
ADMIN_HOME = f'{ADMIN_BPNAME}.AdminHome'

BROADCAST_BPNAME = 'Broadcast'

WATER_BPNAME = 'Water'

DB_CHECK_SQL = 'SELECT COUNT(userid) FROM User;'
DB_BACKUP_TABLES = ['Water']

NOTICE_LEVEL_NAME = {1:'氾濫注意水位', 2:'避難判断水位', 3:'氾濫危険水位'}
NOTICE_LEVEL_COLOR_LINE = {1:['#F2E700', '#000000'], 2:['#FF2800', '#FFFFFF'], 3:['#AA00AA', '#FFFFFF']}

#アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['jpeg','jpg','png','gif','bmp','svg','ico'])

load_dotenv('./.env', encoding='utf-8')
import os
debug = os.environ['DEBUG'] == 'TRUE'
