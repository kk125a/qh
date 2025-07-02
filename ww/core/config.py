import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 数据目录
DATA_DIR = ROOT_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
LOGS_DIR = DATA_DIR / "logs"

# 确保目录存在
for dir_path in [DOCUMENTS_DIR, VECTOR_STORE_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 模型配置
DEFAULT_MODEL = "qwen2.5:7b"
AVAILABLE_MODELS = [
"deepseek-r1:7b",
"qwen2.5:7b",
    "qwen2.5:14b",
    "qwen2.5:72b",
    "llama2:7b",
    "llama2:13b",
    "llama2:70b",
    "mistral:7b",
    "mixtral:8x7b"
]

# Ollama配置
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 模型参数配置
DEFAULT_MODEL_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
    "max_tokens": 2000
}

# 向量数据库配置
CHROMA_SETTINGS = {
    "persist_directory": str(VECTOR_STORE_DIR),
    "anonymized_telemetry": False
}

# 文档处理配置
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

# 检索配置
DEFAULT_SEARCH_PARAMS = {
    "n_results": 5,
    "similarity_threshold": 0.7
}

# 日志配置
LOG_FILE = LOGS_DIR / "app.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# 界面配置
DEFAULT_UI_CONFIG = {
    "enable_knowledge_base": True,
    "show_relevant_docs": True,
    "theme": "light",
    "language": "zh"
} 