# -*- coding: utf-8 -*-
"""
@Project : copilot_demo
@File    : agent.py
@Date    : 2025/12/17 21:05
@Desc    :
"""
from queue import Queue
from typing import List
from langchain.tools import tool
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_openai import ChatOpenAI
# from langchain_classic import hub
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate

from src.copilot.config.const import API_KEY, API_BASE, MODEL
from src.copilot.tools.calculate_tools import calculate_expression
from src.copilot.mcp_client.mcp_client import mcp_client
from src.copilot.schemas.api_schemas import AttachmentInfo
from src.copilot.utils.logger import logger
from src.copilot.utils.files_parse import FileParser
from src.copilot.prompts.chat_prompt import dialogue_react_template

sessions = {}


class MyCustomCallbackHandler(BaseCallbackHandler):
    def __init__(self, que:Queue):
        self.tokens = []
        self.final_output = ""
        self.is_final_answer = False
        self.que = que

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        每当模型生成一个新令牌时调用
        """
        self.tokens.append(token)
        self.final_output += token
        # 这里可以自定义处理，比如打印到标准输出，或者存储到列表等
        self.que.put(token)
        # print(token, end="", flush=True)  # 实时打印每个令牌

    def on_llm_end(self, response, **kwargs) -> None:
        """
        当LLM运行结束时调用
        """
        print("\n流式输出结束")
        self.que.put("~end")
        # 你可以在这里获取完整的文本，即self.final_text

    def on_chain_start(self, inputs, **kwargs) -> None:
        """新的Chain开始时重置状态"""
        self.is_final_answer = False
        self.final_output = ""




class ChatAgent:
    def __init__(self, session_id: str):
        # 对话历史（短期记忆），初始包含系统提示词（定义智能体角色）
        self.session_id = session_id
        self.que = Queue()
        self.attachments = []
        tools = mcp_client.tool_cache.get("bing-cn-mcp_client-server", [])[:1]
        tools.append(calculate_expression)
        prompt = PromptTemplate(template=dialogue_react_template,
                                input_variables=["input", "agent_scratchpad", "chat_history", "tools", "tool_names"])
        self.conversation_history = ChatMessageHistory()
        llm = ChatOpenAI(
            model=MODEL,
            openai_api_key=API_KEY,
            openai_api_base=API_BASE,
            streaming=True,
            callbacks=[MyCustomCallbackHandler(self.que)],
            async_client=True
        )
        self.agent = create_react_agent(llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=self.agent,
                                            tools=tools,
                                            verbose=False,
                                            max_iterations=3,
                                            handle_parsing_errors=True,
                                            return_intermediate_steps=False,
                                            early_stopping_method="generate"
                                            )
        self.agent_with_memory = RunnableWithMessageHistory(
            self.agent_executor,
            self.get_history,  # 传入历史记录获取函数
            input_messages_key="input",
            history_messages_key="chat_history"  # 需要确保提示模板中有此变量
        )

    def parse_attachments(self, attachments_info: List[AttachmentInfo]):
        res = []
        for attachment in attachments_info:
            attachment.content = FileParser.parse_files(attachment.file_path)
            res.append(f'附件名：{attachment.original_name}\n内容：{attachment.content}\n')
        self.attachments.extend(attachments_info)
        return '\n\n'.join(res)

    def get_history(self, session_id: str) -> ChatMessageHistory:
        return self.conversation_history

    def chat(self, user_input):
        result =  self.agent_with_memory.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": self.session_id}}
        )


def get_session(session_id: str) -> ChatAgent:
    if session_id not in sessions:
        sessions[session_id] = ChatAgent(session_id)
    return sessions.get(session_id, ChatAgent(session_id))


def delete_session(session_id: str):
    sessions.pop(session_id)

