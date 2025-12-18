# -*- coding: utf-8 -*-
"""
@Project : copilot_demo
@File    : calculate_tools.py
@Date    : 2025/12/17 21:19
@Desc    : 
"""
from langchain.tools import tool


@tool
def calculate_expression(expression: str) -> str:
    """计算数学表达式的结果，支持加减乘除等基本运算。"""
    try:
        result = eval(expression)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

