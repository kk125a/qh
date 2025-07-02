import sys
from loguru import logger
from datetime import datetime
from pathlib import Path
from .config import LOGS_DIR, MAX_LOG_SIZE, BACKUP_COUNT

# 配置日志系统
logger.remove()  # 移除默认处理器

# 添加控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

def get_chat_log_file() -> Path:
    """获取当前对话的日志文件路径"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return LOGS_DIR / f"chat_{timestamp}.log"

def setup_chat_logger():
    """设置新的对话日志文件"""
    log_file = get_chat_log_file()
    logger.add(
        str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="INFO",
        encoding="utf-8",
        rotation=MAX_LOG_SIZE,
        retention=BACKUP_COUNT
    )
    logger.info(f"开始新的对话，日志文件：{log_file}")
    return log_file

def log_chat(user_input: str, ai_response: str, relevant_docs: list = None):
    """记录对话日志"""
    logger.info(f"用户输入: {user_input}")
    logger.info(f"AI响应: {ai_response}")
    if relevant_docs:
        logger.info(f"相关文档: {relevant_docs}")

def log_file_operation(operation: str, file_name: str, status: str):
    """记录文件操作日志"""
    logger.info(f"文件操作: {operation} | 文件名: {file_name} | 状态: {status}")

def log_error(error: Exception, context: str = None):
    """记录错误日志"""
    logger.error(f"错误: {str(error)} | 上下文: {context}") 