"""数据模型定义"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Pydantic 模型（用于请求/响应校验）

class ItemCreate(BaseModel):
    """创建项目的请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, max_length=500, description="项目描述")


class ItemResponse(BaseModel):
    """项目响应模型"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """错误响应模型"""
    detail: str


# SQLAlchemy 模型（用于数据库映射）

from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base


class Item(Base):
    """项目数据库模型"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="项目名称")
    description = Column(Text, nullable=True, comment="项目描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
