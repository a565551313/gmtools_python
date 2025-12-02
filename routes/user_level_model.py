#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户等级更新请求模型（补充）
"""

from pydantic import BaseModel, Field


class UserLevelUpdateRequest(BaseModel):
    """用户等级更新请求"""
    level: int = Field(..., ge=1, le=10, description="用户等级(1-10)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "level": 5
            }
        }
