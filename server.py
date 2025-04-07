from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hellow": "World"}


@app.post("/chat")
def chat():
    return {"response": "I am a chatbot."}


@app.post("/add_ursl")
def chat():
    return {"response": "URLs added!"}


@app.post("/add_pdfs")
def chat():
    return {"response": "PDFs added!"}


@app.post("/add_text")
def chat():
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
