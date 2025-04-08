from langchain_ollama.chat_models import ChatOllama
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_tools_agent

# from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationTokenBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory


# tool
from my_tools import *

# 导入预设模板
from prompts_template import template_iam_my_god
from prompts_template import emotion_prompt
from prompts_template import emotion_feedback

import os, sys


class Master:
    def __init__(self):
        # 初始化聊天模型，使用指定的模型和温度参数
        self.chatmodel = ChatOllama(model="qwen2.5:7b", temperature=0)

        # 定义内存键，用于存储聊天历史记录
        self.MEMORY_KEY = "chat_history"

        # 系统设定
        self.SYSTEMPL = template_iam_my_god

        # 情绪反馈 提示词
        self.MOODS = emotion_feedback

        # 默认情绪
        self.USER_EMOTION = "default"

        # 定义聊天提示模板，包括系统消息和用户输入
        self.prompt = ChatPromptTemplate.from_messages(
            [
                # 初始化系统提示词 情绪 emotion
                (
                    "system",
                    self.SYSTEMPL.format(
                        who_you_are=self.MOODS[self.USER_EMOTION]["roleSet"]
                    ),
                ),
                # {"system", "{self.MEMORY_KEY}"}, # 聊天历史
                ("user", "{input}"),  # 用户输入占位符
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        self.user_id = "user_test"

        # 初始化内存（目前为空字符串）
        self.memory = self.get_memory(self.user_id)
        memory = ConversationTokenBufferMemory(
            llm=self.chatmodel,
            human_prefix="user",
            ai_prefix="ai",
            memory_key=self.MEMORY_KEY,
            output_key="output",
            return_messages=True,
            # 传入之前的对话记忆
            chat_memory=self.memory,
        )

        # 定义工具列表，包括测试工具和自定义的网络搜索工具, 本地搜索工具
        tool_list = [
            test,
            get_sci_info_from_local_db,
            web_tool,
        ]

        # 创建一个基于 OpenAI 工具的代理
        agent = create_openai_tools_agent(
            llm=self.chatmodel,  # 使用的聊天模型
            tools=tool_list,  # 工具列表
            prompt=self.prompt,  # 提示模板
        )

        # 初始化代理执行器，设置代理和工具，并启用详细日志
        self.agent_executor = AgentExecutor(
            agent=agent, tools=tool_list, memory=memory, verbose=True
        )

    def get_memory(self, user_id: str):

        chat_messages_history = RedisChatMessageHistory(
            session_id=user_id,
            url="redis://localhost:6379/0",
        )

        # print("chat_messages_history:", chat_messages_history)
        store_messages = chat_messages_history.messages

        if len(store_messages) > 6:
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        self.SYSTEMPL
                        + """\n这是你和用户的一段对话，对其进行摘要总结，摘要使用第一人称：我，
                          并提取出其中的用户关键信息，如姓名，年龄，生日, 聊天内容总结等, 按照以下格式返回：
                          总结摘要 | 用户关键信息\n
                          例如：
                          姓名: 小影 \n
                          生日: 1994年1月1日 \n
                          事情：向我问候哦，我礼貌回复，然后他问我今年运势如何，我回答了他今年的运势情况，然后他告辞离开。\n
                          """,
                    ),
                    # 使用占位，替换key
                    # MessagesPlaceholder(variable_name=self.MEMORY_KEY),
                    ("user", "{input}"),
                    # MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
            # 创建一个链式调用，将提示模板与聊天模型连接
            chain = prompt | self.chatmodel
            # 调用链式模型，传入存储的消息和当前用户情绪对应的角色设定，生成摘要
            summary = chain.invoke(
                {
                    "input": store_messages,  # 聊天历史记录作为输入
                    #  # 当前用户情绪对应的角色设定
                    "who_you_are": self.MOODS[self.USER_EMOTION]["roleSet"],
                    # "chat_history": store_messages
                }
            )
            # 打印生成的聊天摘要
            print(f"\n chat summary : \n{summary}")
            # 清空聊天历史记录
            chat_messages_history.clear()
            # 将生成的摘要添加到聊天历史记录中
            chat_messages_history.add_message(summary)
            # 打印更新后的聊天历史记录
            print(f"chat summary post: {chat_messages_history}")

        return chat_messages_history

    def emotion_chain(self, query: str):
        """情绪分析 chain

        Args:
            query (str): 用户输入

        Returns:
            str: 情绪分析结果
        """
        chain = LLMChain(
            name="emotion_analysis_chain",
            prompt=ChatPromptTemplate.from_template(emotion_prompt),
            llm=self.chatmodel,
            output_parser=StrOutputParser(),
        )
        result = chain.invoke({"query": query})
        self.USER_EMOTION = result["text"]
        return result

    def run(self, query):
        """Chat 执行端"""
        # 情绪分析
        emotion = self.emotion_chain(query=query)
        # print(f"{self.emotion_chain.__name__} : {emotion}")
        # print("Role Set: ", self.MOODS[self.USER_EMOTION]["roleSet"])
        print(f"当前用户情绪分析: {emotion["text"]}")

        # 执行代理，传入用户查询，并返回结果
        result = self.agent_executor.invoke(
            {"input": query, self.MEMORY_KEY: self.memory.messages}
        )
        return result
