# 服务器端
接口 --> langchain --> ollama
# 客户端
电报机器人，微信机器人，website
# 接口
http https websocket

# 服务器
1. 接口访问， Python选型fastapi
2. /chat    聊天post请求
3. /add_ursl， 从url中学习知识
4. /add_pdfs， 从pdf中学习知识
5. /add_texts， 从txt中学习知识

# 人性化
1. 用户输入 -> AI判断情绪倾向 ->反馈 -> 获得用户情绪 -> agent判断
2. 工具调用 -> 用户发起请求 -> agent 判断用什么工具 -> 工具使用 -> 返回结果
