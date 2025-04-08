from langchain_ollama.chat_models import ChatOllama
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain.agents import create_openai_tools_agent
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# tool
from my_tools import *

# 导入预设模板
from prompts_template import template_iam_my_god
from prompts_template import emotion_prompt
from prompts_template import emotion_feedback


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
                # {"system", "{chat_history}"}, # 聊天历史
                ("user", "{input}"),  # 用户输入占位符
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # 初始化内存（目前为空字符串）
        self.memory = ""

        # 定义工具列表，包括测试工具和自定义的网络搜索工具
        # tool_list = [test, bocha_websearch_tool, get_info_from_local_db]
        tool_list = [test, bocha_websearch_tool]

        # 创建一个基于 OpenAI 工具的代理
        agent = create_openai_tools_agent(
            llm=self.chatmodel,  # 使用的聊天模型
            tools=tool_list,  # 工具列表
            prompt=self.prompt,  # 提示模板
        )

        # 初始化代理执行器，设置代理和工具，并启用详细日志
        self.agent_executor = AgentExecutor(agent=agent, tools=tool_list, verbose=True)

    def run(self, query):
        """Chat 执行端"""
        # 情绪分析
        emotion = self.emotion_chain(query=query)
        print(f"{self.emotion_chain.__name__} : {emotion}")
        print("Role Set: ", self.MOODS[self.USER_EMOTION]["roleSet"])
        print(f"当前用户情绪分析: {emotion["text"]}")

        # 执行代理，传入用户查询，并返回结果
        result = self.agent_executor.invoke({"input": query})
        return result

    def emotion_chain(self, query: str):
        """情绪分析 chain

        Args:
            query (str): 用户输入

        Returns:
            str: 情绪分析结果
        """
        prompt = emotion_prompt
        chain = LLMChain(
            name="emotion_analysis_chain",
            prompt=ChatPromptTemplate.from_template(emotion_prompt),
            llm=self.chatmodel,
            output_parser=StrOutputParser(),
            verbose=True,
        )
        result = chain.invoke({"query": query})
        self.USER_EMOTION = result["text"]
        return result
