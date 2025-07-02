from typing import List, Dict, Any, Generator
import ollama
from datetime import datetime
from .config import DEFAULT_MODEL, OLLAMA_BASE_URL, DEFAULT_MODEL_PARAMS
from .logger import logger, log_error, log_chat

class ChatManager:
    def __init__(self, model_name: str = DEFAULT_MODEL, model_params: Dict = None):
        self.model = model_name
        self.model_params = model_params or DEFAULT_MODEL_PARAMS
        # 设置ollama客户端
        self.client = ollama.Client(host=OLLAMA_BASE_URL)
        self.conversation_history = []

    def update_model(self, model_name: str, model_params: Dict = None):
        """更新模型和参数"""
        self.model = model_name
        if model_params:
            self.model_params.update(model_params)
        logger.info(f"模型已更新: {model_name}, 参数: {self.model_params}")

    def chat(self, user_input: str, relevant_docs: List[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """处理用户输入并生成流式响应"""
        try:
            # 构建提示词
            prompt = self._build_prompt(user_input, relevant_docs)
            
            # 调用模型生成流式响应
            stream = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=True,
                options={
                    "temperature": self.model_params["temperature"],
                    "top_p": self.model_params["top_p"],
                    "top_k": self.model_params["top_k"],
                    "repeat_penalty": self.model_params["repeat_penalty"],
                    "num_predict": self.model_params["max_tokens"]
                }
            )
            
            # 收集完整响应用于日志记录
            full_response = ""
            
            # 流式输出响应
            for chunk in stream:
                if chunk['response']:
                    full_response += chunk['response']
                    yield chunk['response']
            
            # 记录对话
            log_chat(user_input, full_response, relevant_docs)
            
            # 更新对话历史
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
            
        except Exception as e:
            log_error(e, "生成响应失败")
            raise

    def _build_prompt(self, user_input: str, relevant_docs: List[Dict[str, Any]] = None) -> str:
        """构建提示词"""
        prompt = "你是一个智能助手，请基于以下信息回答用户的问题：\n\n"
        
        if relevant_docs:
            prompt += "相关文档信息：\n"
            for doc in relevant_docs:
                prompt += f"文档：{doc['metadata']['filename']}\n"
                prompt += f"内容：{doc['content']}\n\n"
        
        prompt += f"用户问题：{user_input}\n"
        prompt += "请基于以上信息，给出准确、详细的回答。"
        
        return prompt

    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []
        logger.info("对话历史已清除") 