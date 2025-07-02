from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from .config import CHROMA_SETTINGS
from .logger import logger, log_error

class VectorStore:
    def __init__(self):
        # 使用持久化设置创建客户端
        self.client = chromadb.PersistentClient(path=CHROMA_SETTINGS["persist_directory"])
        # 获取或创建collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("向量存储初始化完成")

    def add_documents(self, documents: List[Dict[str, Any]]):
        """添加文档到向量存储"""
        try:
            ids = [f"{doc['metadata']['filename']}_{doc['metadata']['chunk_id']}" 
                  for doc in documents]
            texts = [doc['content'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]
            
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            logger.info(f"成功添加 {len(documents)} 个文档块到向量存储")
        except Exception as e:
            log_error(e, "添加文档到向量存储失败")
            raise

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = []
            for i in range(len(results['documents'][0])):
                doc = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                }
                documents.append(doc)
            
            logger.info(f"成功搜索到 {len(documents)} 个相关文档")
            return documents
        except Exception as e:
            log_error(e, "搜索文档失败")
            raise

    def delete_documents(self, filename: str):
        """删除指定文件的所有文档块"""
        try:
            # 获取所有文档的元数据
            results = self.collection.get()
            
            # 找到匹配的文档ID
            ids_to_delete = [
                id for id, metadata in zip(results['ids'], results['metadatas'])
                if metadata['filename'] == filename
            ]
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"成功删除文件 {filename} 的所有文档块")
            else:
                logger.warning(f"未找到文件 {filename} 的文档块")
                
        except Exception as e:
            log_error(e, f"删除文档失败: {filename}")
            raise

    def get_all_files(self) -> List[str]:
        """获取所有已存储的文件名"""
        try:
            results = self.collection.get()
            unique_files = set(metadata['filename'] for metadata in results['metadatas'])
            return list(unique_files)
        except Exception as e:
            log_error(e, "获取文件列表失败")
            raise 