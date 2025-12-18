# -*- coding: utf-8 -*-
"""
@Project : chat_demo
@File    : mcp_client.py
@Date    : 2025/12/18 08:40
@Desc    : 
"""
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from enum import Enum
from typing import Union, Optional, Type, Any

from mcp.client.stdio import StdioServerParameters
from mcpadapt.langchain_adapter import LangChainAdapter
from mcpadapt.core import MCPAdapt
from pydantic import BaseModel

from src.copilot.mcp_client.mcp_services_list import mcp_services
from src.copilot.utils.logger import logger


class SseParams(BaseModel):
    url: str


class AdaptType(Enum):
    langchain = LangChainAdapter


exit_stack = ExitStack()


class MCPClient:

    def __init__(self, services_params: dict):
        self.executor = ThreadPoolExecutor()
        self.tool_cache = {}
        asyncio.run(self.init_services(services_params))

    @staticmethod
    def adapt(server_name: str, mcp_param: dict, tool_type: AdaptType):
        if 'url' not in mcp_param:
            param = StdioServerParameters(**mcp_param)
        else:
            param = {"url": mcp_param['url']}
        try:
            adapt_tool = exit_stack.enter_context(
                MCPAdapt(param, tool_type.value())
            )
            for tool in adapt_tool:
                if tool.original_name in mcp_param.get("output_tool", []):
                    tool.result_as_answer = True
            return {server_name: adapt_tool}
        except Exception as e:
            print(f"mcp服务{server_name} 加载失败,参数：{mcp_param},异常:{e}")
            return {"error": str(e)}

    async def init_services(self, servers_params: dict, tool_type: AdaptType = AdaptType.langchain):
        loop = asyncio.get_running_loop()
        tasks = []
        for name, params in servers_params.get("mcpServers", {}).items():
            task = loop.run_in_executor(
                self.executor,
                self.adapt
                *(name, params, tool_type),
            )
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        self.tool_cache = self.tool_cache | {k: v for item in results for k, v in item.items() if k != 'error'}

    def list_tools(self, servers_list: Optional[list[str]] = None):
        tools = []
        tools.extend([tool for name, tools in self.tool_cache.items() for tool in tools if
                      servers_list is None or name in servers_list])
        return tools



mcp_client = MCPClient(mcp_services)  # 初始化MCP工具
pass
