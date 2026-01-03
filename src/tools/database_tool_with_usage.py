"""
通用数据库操作工具（带消耗控制）
提供前端直接读写数据库的通用接口，并记录每次操作的资源消耗
"""
import logging
import json
from typing import Optional
from datetime import datetime
from langchain.tools import tool

from storage.database.db import get_session
from storage.database.shared.model import (
    UserProfile,
    UserAccount,
    DailyReport
)

logger = logging.getLogger(__name__)

# 数据库操作消耗配置
DATABASE_USAGE_COST = {
    "query_user_by_id": 0.1,      # 查询用户：0.1点
    "query_contacts": 0.2,        # 查询联系人：0.2点
    "query_user_reports": 0.2,    # 查询报告：0.2点
    "update_user_profile": 0.5,   # 更新档案：0.5点
    "add_contact": 0.5,           # 添加联系人：0.5点
    "save_report": 1.0,           # 保存报告：1.0点
}


def _record_usage_if_enabled(
    user_id: str,
    action: str,
    enabled: bool = True
):
    """如果启用消耗控制，则记录消耗"""
    if not enabled:
        return

    try:
        # 导入 record_usage 工具
        from tools.usage_limit_tool import record_usage

        # 获取消耗金额
        amount = DATABASE_USAGE_COST.get(action, 0.1)

        # 记录消耗（直接调用工具）
        record_usage.invoke(user_id=user_id, amount=amount)

        logger.info(f"📊 记录消耗 | 用户: {user_id} | 操作: {action} | 消耗: {amount}")

    except Exception as e:
        logger.warning(f"⚠️ 记录消耗失败: {e}")


@tool
def query_user_by_id(
    user_id: str,
    record_usage_enabled: bool = False
) -> str:
    """
    根据用户ID查询用户信息（对应 users 表）

    参数：
    - user_id: 用户ID
    - record_usage_enabled: 是否记录消耗（默认false）

    返回：用户信息（JSON格式）
    """
    try:
        # 记录消耗（如果启用）
        _record_usage_if_enabled(user_id, "query_user_by_id", record_usage_enabled)

        with get_session() as session:
            # 查询用户账户
            account = session.query(UserAccount).filter_by(user_id=user_id).first()
            if not account:
                return f'{{"status": "failed", "error": "用户不存在", "user_id": "{user_id}"}}'

            # 查询用户档案（本人信息）
            profile = session.query(UserProfile).filter_by(
                user_id=user_id,
                relationship_type="self"
            ).first()

            # 构建返回数据
            result = {
                "status": "success",
                "user_id": account.user_id,
                "username": account.username,
                "is_admin": account.is_admin,
                "created_at": account.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "last_login_at": account.last_login_at.strftime("%Y-%m-%d %H:%M:%S") if account.last_login_at else None,
                "profile": None
            }

            if profile:
                result["profile"] = {
                    "id": profile.id,
                    "name": profile.name,
                    "gender": profile.gender,
                    "birth_date": profile.birth_date,
                    "mbti": profile.mbti,
                    "birth_place": profile.birth_place,
                    "current_location": profile.current_location,
                    "company_name": profile.company_name,
                    "company_type": profile.company_type,
                    "job_title": profile.job_title,
                    "job_level": profile.job_level,
                    "photo_url": profile.photo_url,
                    "notes": profile.notes
                }

            logger.info(f"✅ 查询用户成功 | user_id: {user_id} | 记录消耗: {record_usage_enabled}")
            return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ 查询用户失败: {e}")
        return f'{{"status": "failed", "error": "{str(e)}"}}'
