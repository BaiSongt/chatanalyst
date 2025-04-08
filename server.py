from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from ZhangMaster import Master

app = FastAPI()


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
    import uvicorn, os, sys

    # Add the root directory to the Python path
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

    uvicorn.run(app, host="0.0.0.0", port=8000)
