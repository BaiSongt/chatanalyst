from langchain.agents import tool
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain_ollama.embeddings import OllamaEmbeddings
from bocha_api import bocha_websearch_tool

@tool
def test():
    """test tool"""
    return "test tools"


@tool
def get_info_from_local_db(query: str):
    """当问到和机器学习相关的内容时，优先使用本地数据进行检索回答"""
    """
    使用指定的查询字符串查询本地数据库。

    此函数使用 Qdrant 客户端从本地数据库中检索相关文档。
    它采用 "mmr"（最大边际相关性）搜索类型，根据提供的查询检索文档。

    参数:
        query (str): 用于搜索本地数据库的查询字符串。

    返回:
        list: 从本地数据库中检索到的相关文档列表。
    """

    client = Qdrant(
        QdrantClient(path="/local_qdrand"),
        "local_documents",
        OllamaEmbeddings(model="bge-m3:latest"),
    )
    retriever = client.as_retriever(search_type="mmr")
    result = retriever.get_relevant_documents(query)
    return result
