# -*- coding: utf-8 -*-
"""
@Project : copilot_demo
@File    : const.py
@Date    : 2025/12/17 21:02
@Desc    : 
"""
import os

API_KEY =os.environ.get('OPENAI_API_KEY', 'ms-e194cf97-584f-4e90-a7d3-f523d0bf1806')

if os.environ.get("OPENAI_BASE_URL"):
    API_BASE = os.environ.get("OPENAI_BASE_URL")
else:
    if os.environ.get('OPENAI_API_KEY'):
        API_BASE = "https://api.openai.com/v1"
    else:
        API_BASE = "https://api-inference.modelscope.cn/v1"
MODEL = os.environ.get("MODEL", "Qwen/Qwen3-32B")