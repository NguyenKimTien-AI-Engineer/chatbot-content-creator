from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import pytz

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from mem0 import Memory

from configs import constant

load_dotenv()

# ================================================
# EMBEDDINGS

# OpenAI Embeddings
embeddings_model = OpenAIEmbeddings()

# Local Embeddings
# model_name = "BAAI/bge-large-en"
# model_kwargs = {"device": "cpu"}
# encode_kwargs = {"normalize_embeddings": True}
# embeddings_model = HuggingFaceBgeEmbeddings(
#     model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
# )

# Embeddings model for chunking
# chunk_model_name = "sentence-transformers/all-MiniLM-L6-v2"
# chunk_embeddings_model = SentenceTransformerEmbeddings(model_name=model_name)


# ================================================
# MEMORY
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": constant.QDRANT_HOST,
            "port": constant.QDRANT_PORT,
        }
    }
}

# memory = Memory.from_config(config)
# memory = Memory()  # Temporarily disabled due to Qdrant lock issue
memory = None  # Placeholder for now

# ================================================
translator = GoogleTranslator(source='auto', target='en')

vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

# ================================================
# LLM

llm = ChatOpenAI(model="gpt-4.1", temperature=0)
llm_stream = ChatOpenAI(model="gpt-4.1", temperature=0, streaming=True)
llm_mini = ChatOpenAI(model="gpt-4.1-mini", temperature=0)


# ================================================
# VLLM

# llm = VLLMOpenAI(
#     openai_api_key=_constants.VLLM_TOKEN,
#     openai_api_base=_constants.VLLM_PATH,
#     model_name="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
#     temperature=0,
#     top_p=0.95,
#     batch_size=128,
#     max_tokens=2048,
#     streaming=False,
# )
#
# llm_stream = VLLMOpenAI(
#     openai_api_key=_constants.VLLM_TOKEN,
#     openai_api_base=_constants.VLLM_PATH,
#     model_name="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
#     temperature=0,
#     top_p=0.95,
#     batch_size=128,
#     max_tokens=2048,
#     frequency_penalty=0.1,
#     presence_penalty=0.1,
#     streaming=True,
# )


# ================================================
# FUNCTIONS
def get_llm(model="gpt-4.1", temperature=0, streaming=False):
    if model == "gpt-4.1-mini":
        return llm_mini
    elif model == "gpt-4.1" and streaming:
        return llm_stream
    elif model == "gpt-4.1":
        return llm
    return ChatOpenAI(model=model, temperature=temperature, streaming=streaming)


def get_embedding():
    return embeddings_model



