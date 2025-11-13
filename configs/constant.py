import os
from dotenv import load_dotenv

load_dotenv()

# ================================================
# SERVER
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")

# ================================================
# CONFIGS
MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_NUM_TOKEN = 70000

NODE_CHUNK_SIZE_TYPE_1 = 128
NODE_CHUNK_SIZE_TYPE_2 = 256
NODE_CHUNK_SIZE_TYPE_3 = 512
NODE_CHUNK_SIZE_TYPE_4 = 1024
NODE_CHUNK_SIZE_TYPE_5 = 1536
NODE_CHUNK_SIZE_TYPE_6 = 2048

# ================================================
# CHATBOT
CHATBOT_NAME = "CHATBOT"

#
MODEL_CHATBOT_BASIC = "gpt-4.1"
MODEL_CHATBOT_REFERENCE = "gpt-4.1"
MODEL_CHATBOT_CHART = "gpt-4.1"
MODEL_CHATBOT_SUGGESTION = "gpt-4.1-mini"
MODEL_CHATBOT_CUSTOM_PROMPT = "gpt-4.1"
MODEL_PROVINCE_MERGER = "gpt-4.1"
MODEL_KAT = "gpt-4.1"
MODEL_SCHOOL = "gpt-4.1"
MODEL_SUMMARY = "gpt-4.1-mini"

K_CHATBOT_BASIC = 10
K_CHATBOT_REFERENCE = 10
K_CHATBOT_CHART = 10
K_CHATBOT_CUSTOM_PROMPT = 10
K_PROVINCE_MERGER = 5
K_KAT = 5
K_SCHOOL = 5

# ================================================
# PATH
DATA = "./resources/data"
DATA_USER = "./resources/data/user"
DATA_PUBLIC = "./resources/data/public"

DATA_HISTORY = "./resources/data/history"

DATA_TOKEN = "./resources/data/token"

DATA_CHART = "./resources/tmp/chart"
DATA_TMP = "./resources/tmp"

LOG = "./resources/logs"

ALL_DATA_UPLOAD = "./resources/data/all_qdrant_collections.json"

# ================================================
# QDRANT
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")
QDRANT_SERVER = os.getenv("QDRANT_SERVER")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# MongoDB
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_CONNECTION = os.getenv("MONGODB_CONNECTION")

# MYSQL
MYSQL_DB_HOST = os.getenv("MYSQL_DB_HOST")
MYSQL_DB_NAME = os.getenv("MYSQL_DB_NAME")
MYSQL_DB_USER = os.getenv("MYSQL_DB_USER")
MYSQL_DB_PASSWORD = os.getenv("MYSQL_DB_PASSWORD")

# ================================================
# VLLM
VLLM_URL = os.getenv("VLLM_URL")
VLLM_TOKEN = os.getenv("VLLM_TOKEN")

# ================================================
# AWS
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")


