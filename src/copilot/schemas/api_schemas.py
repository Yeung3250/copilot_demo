# -*- coding: utf-8 -*-
"""
@Project : copilot_demo
@File    : api_schemas.py
@Date    : 2025/12/17 21:31
@Desc    : 
"""
from pydantic import BaseModel, Field
from typing import Optional, List  # 新增List导入

# Pydantic模型定义
class AttachmentInfo(BaseModel):
    """附件信息模型（可选）"""
    original_name: Optional[str] = Field(None, description="附件原始名称")
    file_path: Optional[str] = Field(None, description="附件访问路径")
    content: Optional[str] = Field('', description="附件内容")


class ChatRequest(BaseModel):
    """AI对话请求模型"""
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="用户输入的内容")
    attachments: Optional[List[AttachmentInfo]] = Field([], description="附件信息列表（可为空）")  # 改为列表

class CleanRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")