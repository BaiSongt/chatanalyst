from langchain.agents import tool
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from bocha_api import bocha_websearch_tool

import requests, json, os

from langchain_core.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_ollama.embeddings import OllamaEmbeddings

from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader


@tool
def test():
    """test tool"""
    return "test tools"


@tool
def web_tool(query: str, count: int):
    """网络搜索工具，询问到实时信息和不知道的事情时，使用该工具"""
    result = bocha_websearch_tool(query, count)
    return result


@tool
def get_sci_info_from_local_db(query: str):
    """当问到和科学技术相关的内容时，优先使用本地数据进行检索回答
    当没有查询到问题相关内容，或者信息较少时，可以使用其他工具
    """
    """
    使用指定的查询字符串查询本地数据库。

    参数:
        query (str): 用于搜索本地数据库的查询字符串。

    返回:
        list: 从本地数据库中检索到的相关文档列表。
    """

    print("> Tool call: get_sci_info_from_local_db")

    client = Qdrant(
        QdrantClient(path=os.path.abspath(os.path.join(os.getcwd(), "local_qdrand"))),
        "local_documents_db",
        OllamaEmbeddings(model="bge-m3:latest"),
    )
    # 此函数使用 Qdrant 客户端从本地数据库中检索相关文档。
    # 它采用 "mmr"（最大边际相关性）搜索类型，根据提供的查询检索文档。
    retriever = client.as_retriever(search_type="mmr")
    result = retriever.get_relevant_documents(query)
    return result


@tool
def dream_analysis(query: str):
    """这是一个解梦的工具，用户需要解梦时调用该工具，用户需要提供梦惊相关内容，否则该工具不可用"""
    api_key = "YOUR_API_KEY"
    url = f"https://api............."
    LLM = OllamaLLM(model="qwen2.5:7b", temperature=0)
    prompt = PromptTemplate.from_template(
        "根据内容提取一个1个关键词， 只返回关键词， 内容为{topic}"
    )
    prompt_value = prompt.invoke({"topic": query})

    keyword = LLM.invoke(prompt_value)
    print("提取的关键词为：", keyword)
    result = requests.post(url, data={"api_key": api_key, "title_zhougong": keyword})
    if result.status_code == 200:
        json_result = json.loads(result.json())
        return json_result
    else:
        raise ConnectionError("无法连接请求，请稍后再试")


def doc_db_creator(
    loader,
    separators="\n",
    chunk_size=400,
    chunk_overlap=50,
):
    docs = loader.load()
    url_documents = RecursiveCharacterTextSplitter(
        separators=separators,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    ).split_documents(docs)

    # 引入向量数据库
    qdrant = Qdrant.from_documents(
        documents=url_documents,
        embedding=OllamaEmbeddings(model="bge-m3:latest"),
        path=os.path.abspath(os.path.join(os.getcwd(), "local_qdrand")),
        collection_name="local_documents_db",
    )


def load_url(url: str):
    loader = WebBaseLoader(url)
    doc_db_creator(loader=loader, separators=[",", ".", "\n"])
    print("> URL DB created successful!")
    return {"response": "URLs added!"}


def load_pdf(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    doc_db_creator(loader=loader, separators=[",", ".", "，", "。", "\n"])
    print("> PDF DB created successful!")
    return {"response": "PDFs added!"}


def load_text(text_path: str):
    loader = TextLoader(text_path)
    doc_db_creator(loader=loader, separators=[",", ".", "，", "。", "\n"])
    print("> Text DB created successful!")
    return {"response": "Texts added!"}


# def load_excel(self, pdf_path:str):
    # loader = PyPDFLoader(pdf_path)
    # doc_db_creator(loader=loader, separators=[',','.','，','。','\n'])
    # print("> PDF DB created successful!")
    # return {"response": "PDFs added!"}
