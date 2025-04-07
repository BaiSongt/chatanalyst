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
        self.chatmodel = ChatOllama(model="qwen2.5:7b", temperature=0)

        self.MEMORY_KEY = "chat_history"

        self.SYSTEMPL = ""

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个助手"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ]
        )

        self.memory = ""

        test_tool = [test, bocha_websearch_tool]
        agent = create_openai_tools_agent(
            llm=self.chatmodel,
            tools=test_tool,
            prompt=self.prompt
        )

        self.agent_executor = AgentExecutor(agent=agent, tools=test_tool, verbose=True)

    def run(self, query):
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
