import os


BACKEND_URL = os.environ.get('BACKEND_URL')
SYSTEM_TOKEN = os.environ.get('SYSTEM_TOKEN')
# BACKEND_URL = 'http://127.0.0.1:8001'

FILES_BUCKET_FOLDER = os.environ.get('FILES_BUCKET_FOLDER')
FILES_BUCKET_NAME = 'daohq-files'

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
# BACKEND_URL = os.environ.get('RENDER_URL')
RENDER_URL = 'http://127.0.0.1:8010'