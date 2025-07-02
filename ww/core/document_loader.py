from pathlib import Path
from typing import List, Dict, Any
import docx
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from .config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from .logger import logger, log_error

class DocumentLoader:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=DEFAULT_CHUNK_SIZE,
            chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            length_function=len,
        )

    def load_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """加载文档并分块"""
        try:
            file_extension = file_path.suffix.lower()
            content = self._read_file(file_path, file_extension)
            
            # 分块处理
            chunks = self.text_splitter.split_text(content)
            
            # 为每个块添加元数据
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    "content": chunk,
                    "metadata": {
                        "source": str(file_path),
                        "filename": file_path.name,
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    }
                }
                documents.append(doc)
            
            logger.info(f"成功加载文档: {file_path.name}, 生成了 {len(documents)} 个块")
            return documents
            
        except Exception as e:
            log_error(e, f"加载文档失败: {file_path}")
            raise

    def _read_file(self, file_path: Path, file_extension: str) -> str:
        """根据文件类型读取内容"""
        try:
            if file_extension == '.pdf':
                return self._read_pdf(file_path)
            elif file_extension == '.docx':
                return self._read_docx(file_path)
            elif file_extension in ['.txt', '.md']:
                return self._read_text(file_path)
            else:
                raise ValueError(f"不支持的文件类型: {file_extension}")
        except Exception as e:
            log_error(e, f"读取文件失败: {file_path}")
            raise

    def _read_pdf(self, file_path: Path) -> str:
        """读取PDF文件"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text

    def _read_docx(self, file_path: Path) -> str:
        """读取DOCX文件"""
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def _read_text(self, file_path: Path) -> str:
        """读取文本文件"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read() 