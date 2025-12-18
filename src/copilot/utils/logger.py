# -*- coding: utf-8 -*-
"""
@Project : chat_demo
@File    : logger.py
@Date    : 2025/12/15 09:17
@Desc    : 
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from loguru import logger

from src.copilot.config.config import base_dir

logs_path = os.path.join(base_dir, "logs")

# 定位到log日志文件
if not os.path.exists(logs_path):
    os.mkdir(logs_path)

log_path_info = os.path.join(logs_path, f'{time.strftime("%Y-%m-%d")}_info.log')
log_path_error = os.path.join(logs_path, f'{time.strftime("%Y-%m-%d")}_error.log')

# 日志简单配置 文件区分不同级别的日志
logger.add(log_path_info, rotation="500 MB", encoding='utf-8', enqueue=True, level='INFO')
logger.add(log_path_error, rotation="500 MB", encoding='utf-8', enqueue=True, level='ERROR')

__all__ = ["logger"]
