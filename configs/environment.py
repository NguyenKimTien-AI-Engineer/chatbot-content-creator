import os

from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import os
import pytz

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from mem0 import Memory

from configs import constant

load_dotenv()

GOOGLE_API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
    or ""
)
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
GEMINI_CHAT_MODEL_MINI = os.getenv("GEMINI_CHAT_MODEL_MINI", "gemini-2.5-flash-lite")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")

# ================================================
# EMBEDDINGS
embeddings_model = GoogleGenerativeAIEmbeddings(
    model=GEMINI_EMBEDDING_MODEL,
    google_api_key=GOOGLE_API_KEY,
)

# ================================================
# MEMORY
def _init_memory():
    if not GOOGLE_API_KEY:
        return None

    memory_config = {
        "llm": {
            "provider": "gemini",
            "config": {
                "model": GEMINI_CHAT_MODEL,
                "temperature": 0,
                "api_key": GOOGLE_API_KEY,
            },
        },
        "embedder": {
            "provider": "gemini",
            "config": {
                "model": GEMINI_EMBEDDING_MODEL,
                "api_key": GOOGLE_API_KEY,
            },
        },
    }

    if constant.QDRANT_HOST:
        memory_config["vector_store"] = {
            "provider": "qdrant",
            "config": {
                "host": constant.QDRANT_HOST,
                "port": int(constant.QDRANT_PORT or 6333),
            },
        }

    try:
        return Memory.from_config(memory_config)
    except Exception as err:
        print(f"Memory init skipped: {err}")
        return None


memory = _init_memory()

# ================================================
translator = GoogleTranslator(source='auto', target='en')

vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

# ================================================
# LLM
_llm_kwargs = {"google_api_key": GOOGLE_API_KEY, "temperature": 0}

llm = ChatGoogleGenerativeAI(model=GEMINI_CHAT_MODEL, **_llm_kwargs)
llm_stream = ChatGoogleGenerativeAI(
    model=GEMINI_CHAT_MODEL,
    streaming=True,
    **_llm_kwargs,
)
llm_mini = ChatGoogleGenerativeAI(model=GEMINI_CHAT_MODEL_MINI, **_llm_kwargs)

_LEGACY_MODEL_MAP = {
    "gpt-4.1": GEMINI_CHAT_MODEL,
    "gpt-4.1-mini": GEMINI_CHAT_MODEL_MINI,
    "gpt-4o": GEMINI_CHAT_MODEL,
    "gemini-2.0-flash": GEMINI_CHAT_MODEL,
    "gemini-2.0-flash-lite": GEMINI_CHAT_MODEL_MINI,
}


def _resolve_model(model: str) -> str:
    return _LEGACY_MODEL_MAP.get(model, model)


def get_llm(model="gemini-2.5-flash", temperature=0, streaming=False):
    resolved = _resolve_model(model)

    if streaming:
        return ChatGoogleGenerativeAI(
            model=resolved,
            temperature=temperature,
            streaming=True,
            google_api_key=GOOGLE_API_KEY,
        )

    if resolved == GEMINI_CHAT_MODEL_MINI:
        return llm_mini
    if resolved == GEMINI_CHAT_MODEL:
        return llm

    return ChatGoogleGenerativeAI(
        model=resolved,
        temperature=temperature,
        streaming=False,
        google_api_key=GOOGLE_API_KEY,
    )


def get_embedding():
    return embeddings_model
