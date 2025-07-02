import streamlit as st
from pathlib import Path
import shutil
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.document_loader import DocumentLoader
from core.vector_store import VectorStore
from core.chat import ChatManager
from core.config import (
    DOCUMENTS_DIR, DEFAULT_MODEL, AVAILABLE_MODELS,
    DEFAULT_MODEL_PARAMS, DEFAULT_UI_CONFIG, DEFAULT_SEARCH_PARAMS
)
from core.logger import logger, log_error, setup_chat_logger

# 确保文档目录存在
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.log_file = setup_chat_logger()
    st.session_state.model_params = DEFAULT_MODEL_PARAMS.copy()
    st.session_state.ui_config = DEFAULT_UI_CONFIG.copy()
    st.session_state.search_params = DEFAULT_SEARCH_PARAMS.copy()
    st.session_state.current_model = DEFAULT_MODEL

# 初始化组件
document_loader = DocumentLoader()
vector_store = VectorStore()
chat_manager = ChatManager(
    model_name=st.session_state.current_model,
    model_params=st.session_state.model_params
)

def save_uploaded_file(uploaded_file):
    """保存上传的文件"""
    try:
        file_path = DOCUMENTS_DIR / uploaded_file.name
        if file_path.exists():
            file_path.unlink()
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logger.info(f"文件已保存: {file_path}")
        return file_path
    except Exception as e:
        log_error(e, f"保存文件失败: {uploaded_file.name}")
        raise

def process_file(file_path: Path):
    """处理文件并添加到向量存储"""
    try:
        documents = document_loader.load_document(file_path)
        vector_store.add_documents(documents)
        return True
    except Exception as e:
        log_error(e, f"处理文件失败: {file_path}")
        return False

def delete_file(filename: str):
    """删除文件及其向量存储"""
    try:
        file_path = DOCUMENTS_DIR / filename
        if file_path.exists():
            file_path.unlink()
        vector_store.delete_documents(filename)
        return True
    except Exception as e:
        log_error(e, f"删除文件失败: {filename}")
        return False

# 设置页面标题
st.set_page_config(page_title="智能文档问答系统", layout="wide")
st.title("智能文档问答系统")

# 创建侧边栏
with st.sidebar:
    # 设置选项卡
    tab1, tab2 = st.tabs(["文件管理", "系统设置"])
    
    with tab1:
        st.header("文件管理")
        
        # 文件上传
        uploaded_files = st.file_uploader(
            "上传文件",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if st.button(f"处理 {uploaded_file.name}"):
                    with st.spinner(f"正在处理 {uploaded_file.name}..."):
                        file_path = save_uploaded_file(uploaded_file)
                        if process_file(file_path):
                            st.success(f"{uploaded_file.name} 处理成功！")
                        else:
                            st.error(f"{uploaded_file.name} 处理失败！")
        
        # 显示已存储的文件
        st.subheader("已存储的文件")
        stored_files = vector_store.get_all_files()
        if stored_files:
            for filename in stored_files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(filename)
                with col2:
                    if st.button("删除", key=f"delete_{filename}"):
                        if delete_file(filename):
                            st.success(f"{filename} 删除成功！")
                            st.rerun()
                        else:
                            st.error(f"{filename} 删除失败！")
    
    with tab2:
        st.header("系统设置")
        
        # 模型选择
        st.subheader("模型设置")
        selected_model = st.selectbox(
            "选择模型",
            AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(st.session_state.current_model)
        )
        
        if selected_model != st.session_state.current_model:
            st.session_state.current_model = selected_model
            chat_manager.update_model(selected_model, st.session_state.model_params)
            st.success(f"模型已更新为: {selected_model}")
        
        # 模型参数设置
        st.subheader("模型参数")
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.model_params["temperature"],
                step=0.1
            )
            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.model_params["top_p"],
                step=0.1
            )
        with col2:
            top_k = st.slider(
                "Top K",
                min_value=1,
                max_value=100,
                value=st.session_state.model_params["top_k"]
            )
            repeat_penalty = st.slider(
                "Repeat Penalty",
                min_value=1.0,
                max_value=2.0,
                value=st.session_state.model_params["repeat_penalty"],
                step=0.1
            )
        
        # 更新模型参数
        new_params = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repeat_penalty": repeat_penalty,
            "max_tokens": st.session_state.model_params["max_tokens"]
        }
        if new_params != st.session_state.model_params:
            st.session_state.model_params = new_params
            chat_manager.update_model(st.session_state.current_model, new_params)
            st.success("模型参数已更新")
        
        # 界面设置
        st.subheader("界面设置")
        st.session_state.ui_config["enable_knowledge_base"] = st.checkbox(
            "启用知识库",
            value=st.session_state.ui_config["enable_knowledge_base"]
        )
        st.session_state.ui_config["show_relevant_docs"] = st.checkbox(
            "显示相关文档",
            value=st.session_state.ui_config["show_relevant_docs"]
        )
        
        # 检索设置
        st.subheader("检索设置")
        st.session_state.search_params["n_results"] = st.slider(
            "检索结果数量",
            min_value=1,
            max_value=10,
            value=st.session_state.search_params["n_results"]
        )
        st.session_state.search_params["similarity_threshold"] = st.slider(
            "相似度阈值",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.search_params["similarity_threshold"],
            step=0.1
        )

# 主界面
st.header("对话")

# 显示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("请输入您的问题"):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 搜索相关文档
    relevant_docs = None
    if st.session_state.ui_config["enable_knowledge_base"]:
        relevant_docs = vector_store.search(
            prompt,
            n_results=st.session_state.search_params["n_results"]
        )
    
    # 生成响应
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 流式输出响应
        for chunk in chat_manager.chat(prompt, relevant_docs):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # 显示相关文档
    if relevant_docs and st.session_state.ui_config["show_relevant_docs"]:
        with st.expander("查看相关文档"):
            for doc in relevant_docs:
                st.markdown(f"**文档：{doc['metadata']['filename']}**")
                st.markdown(doc['content'])
                st.markdown("---") 