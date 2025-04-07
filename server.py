from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import initialize_agent, AgentType, AgentExecutor, tool
from langchain.agents import create_openai_tools_agent
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from bocha_api import bocha_websearch_tool

app = FastAPI()


@tool
def test():
    """test tool"""
    return "test tools"


class Master:
    def __init__(self):
        # 初始化聊天模型，使用指定的模型和温度参数
        self.chatmodel = ChatOllama(model="qwen2.5:7b", temperature=0)

        # 定义内存键，用于存储聊天历史记录
        self.MEMORY_KEY = "chat_history"

        # 系统提示词（目前为空字符串）
        self.SYSTEMPL = ""

        # 定义聊天提示模板，包括系统消息和用户输入
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个助手"),  # 系统消息，定义助手的角色
                ("user", "{input}"),  # 用户输入占位符
                MessagesPlaceholder(
                    variable_name="agent_scratchpad"
                ),  # 占位符，用于代理的临时数据
            ]
        )

        # 初始化内存（目前为空字符串）
        self.memory = ""

        # 定义工具列表，包括测试工具和自定义的网络搜索工具
        test_tool = [test, bocha_websearch_tool]

        # 创建一个基于 OpenAI 工具的代理
        agent = create_openai_tools_agent(
            llm=self.chatmodel,  # 使用的聊天模型
            tools=test_tool,  # 工具列表
            prompt=self.prompt,  # 提示模板
        )

        # 初始化代理执行器，设置代理和工具，并启用详细日志
        self.agent_executor = AgentExecutor(agent=agent, tools=test_tool, verbose=True)

    def run(self, query):
        # 执行代理，传入用户查询，并返回结果
        result = self.agent_executor.invoke({"input": query})
        return result


@app.get("/")
def read_root():
    return {"Hellow": "World"}


@app.post("/chat")
def chat(query: str):
    master = Master()
    return master.run(query)


@app.post("/add_ursl")
def add_ursl():
    return {"response": "URLs added!"}


@app.post("/add_pdfs")
def add_pdfs():
    return {"response": "PDFs added!"}


@app.post("/add_text")
def add_text():
    return {"response": "Texts added!"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # 接受 WebSocket 连接
    try:
        while True:
            data = await websocket.receive_text()  # 接收来自客户端的文本消息
            await websocket.send_text(
                f"Message text was: {data}"
            )  # 将接收到的消息回传给客户端
    except WebSocketDisconnect:
        print("Connection closed")  # 打印连接关闭的消息
        await websocket.close()  # 关闭 WebSocket 连接


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
