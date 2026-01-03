"""
消耗限制工具
提供消耗检查和记录功能，防止资源过度消耗
"""
import logging
from datetime import datetime, date
from typing import Optional
from langchain.tools import tool

from storage.database.db import get_session
from storage.database.shared.model import UserAccount, UserDailyUsage, GlobalDailyUsage

logger = logging.getLogger(__name__)

# 消耗限制配置
USAGE_LIMITS = {
    "global_daily_limit": 1000,  # 全局每日消耗限制
    "user_daily_limit": 300,     # 单用户每日消耗限制
}


@tool
def check_global_usage_limit(
    user_id: str
) -> str:
    """
    检查全局今日消耗是否已超限

    参数：
    - user_id: 用户ID（用于日志记录）

    返回：检查结果
    """
    try:
        with get_session() as session:
            today = date.today().strftime("%Y-%m-%d")

            # 获取今日全局消耗记录
            global_usage = session.query(GlobalDailyUsage).filter_by(date=today).first()

            # 如果今日记录不存在，初始化为0
            if not global_usage:
                global_usage = GlobalDailyUsage(
                    date=today,
                    total_usage=0,
                    updated_at=datetime.utcnow()
                )
                session.add(global_usage)
                session.commit()

            current_usage = global_usage.total_usage
            limit = USAGE_LIMITS["global_daily_limit"]
            remaining = limit - current_usage

            if current_usage >= limit:
                logger.warning(f"⚠️ 全局消耗已超限 | 用户: {user_id} | 今日消耗: {current_usage}/{limit}")
                return f"""❌ 全局消耗已超限

**今日总消耗**: {current_usage}
**消耗限制**: {limit}
**状态**: 超限
**提示**: 当日访问已超限，请明天再来
"""

            logger.info(f"✅ 全局消耗正常 | 用户: {user_id} | 今日消耗: {current_usage}/{limit}")
            return f"""✅ 全局消耗正常

**今日总消耗**: {current_usage}
**消耗限制**: {limit}
**剩余额度**: {remaining}
**状态**: 正常
"""


    except Exception as e:
        logger.error(f"❌ 检查全局消耗失败: {e}")
        return f"❌ 检查失败：{str(e)}"


@tool
def check_user_usage_limit(
    user_id: str
) -> str:
    """
    检查用户今日消耗是否已超限（管理员无限制）

    参数：
    - user_id: 用户ID

    返回：检查结果
    """
    try:
        with get_session() as session:
            # 检查是否为管理员（管理员无限制）
            user = session.query(UserAccount).filter_by(user_id=user_id).first()
            if user and user.is_admin:
                logger.info(f"✅ 管理员用户，无消耗限制 | 用户ID: {user_id}")
                return f"""✅ 管理员账户，无消耗限制

**用户ID**: {user_id}
**用户名**: {user.username}
**提示**: 管理员账户无消耗限制
"""

            today = date.today().strftime("%Y-%m-%d")

            # 获取用户今日消耗记录
            user_usage = session.query(UserDailyUsage).filter_by(user_id=user_id, date=today).first()

            # 如果今日记录不存在，初始化为0
            if not user_usage:
                user_usage = UserDailyUsage(
                    user_id=user_id,
                    date=today,
                    usage=0,
                    updated_at=datetime.utcnow()
                )
                session.add(user_usage)
                session.commit()

            current_usage = user_usage.usage
            limit = USAGE_LIMITS["user_daily_limit"]
            remaining = limit - current_usage

            if current_usage >= limit:
                logger.warning(f"⚠️ 用户消耗已超限 | 用户: {user_id} | 今日消耗: {current_usage}/{limit}")
                return f"""❌ 用户消耗已超限

**用户ID**: {user_id}
**今日消耗**: {current_usage}
**消耗限制**: {limit}
**状态**: 超限
**提示**: 当日访问已超限，请明天再来
"""

            logger.info(f"✅ 用户消耗正常 | 用户: {user_id} | 今日消耗: {current_usage}/{limit}")
            return f"""✅ 用户消耗正常

**用户ID**: {user_id}
**今日消耗**: {current_usage}
**消耗限制**: {limit}
**剩余额度**: {remaining}
**状态**: 正常
"""


    except Exception as e:
        logger.error(f"❌ 检查用户消耗失败: {e}")
        return f"❌ 检查失败：{str(e)}"


@tool
def record_usage(
    user_id: str,
    amount: int = 1
) -> str:
    """
    记录用户消耗（包含全局消耗和用户消耗）

    参数：
    - user_id: 用户ID
    - amount: 消耗数量（默认1）

    返回：记录结果
    """
    try:
        if amount <= 0:
            return f"""❌ 无效的消耗数量

**错误**: 消耗数量必须大于0
**提供的值**: {amount}
"""

        with get_session() as session:
            today = date.today().strftime("%Y-%m-%d")

            # 1. 更新全局消耗
            global_usage = session.query(GlobalDailyUsage).filter_by(date=today).first()
            if not global_usage:
                global_usage = GlobalDailyUsage(
                    date=today,
                    total_usage=0,
                    updated_at=datetime.utcnow()
                )
                session.add(global_usage)

            global_usage.total_usage += amount
            global_usage.updated_at = datetime.utcnow()

            # 2. 更新用户消耗
            user_usage = session.query(UserDailyUsage).filter_by(user_id=user_id, date=today).first()
            if not user_usage:
                user_usage = UserDailyUsage(
                    user_id=user_id,
                    date=today,
                    usage=0,
                    updated_at=datetime.utcnow()
                )
                session.add(user_usage)

            user_usage.usage += amount
            user_usage.updated_at = datetime.utcnow()

            session.commit()

            logger.info(f"✅ 消耗记录成功 | 用户: {user_id} | 消耗: {amount}")
            return f"""✅ 消耗记录成功

**用户ID**: {user_id}
**消耗数量**: {amount}
**用户今日消耗**: {user_usage.usage}
**全局今日消耗**: {global_usage.total_usage}
"""


    except Exception as e:
        logger.error(f"❌ 记录消耗失败: {e}")
        return f"❌ 记录失败：{str(e)}"


@tool
def get_usage_statistics(
    admin_user_id: str,
    date_str: Optional[str] = None
) -> str:
    """
    获取消耗统计信息（仅管理员可调用）

    参数：
    - admin_user_id: 管理员用户ID
    - date_str: 日期（格式：YYYY-MM-DD，不指定则查询今天）

    返回：统计信息
    """
    try:
        # 验证是否为管理员
        with get_session() as session:
            admin = session.query(UserAccount).filter_by(user_id=admin_user_id).first()
            if not admin or not admin.is_admin:
                return "❌ 权限不足：只有管理员可以查看消耗统计"

            # 确定查询日期
            query_date = date_str if date_str else date.today().strftime("%Y-%m-%d")

            # 1. 获取全局消耗
            global_usage = session.query(GlobalDailyUsage).filter_by(date=query_date).first()
            global_total = global_usage.total_usage if global_usage else 0

            # 2. 获取所有用户的消耗
            user_usages = session.query(UserDailyUsage).filter_by(date=query_date).all()

            # 3. 统计信息
            total_users = len(user_usages)
            avg_usage = global_total / total_users if total_users > 0 else 0
            top_users = sorted(user_usages, key=lambda x: x.usage, reverse=True)[:10]

            # 格式化输出
            lines = [
                f"📊 消耗统计信息",
                "",
                f"**日期**: {query_date}",
                f"**全局总消耗**: {global_total}",
                f"**消耗限制**: {USAGE_LIMITS['global_daily_limit']}",
                f"**使用率**: {global_total / USAGE_LIMITS['global_daily_limit'] * 100:.1f}%",
                "",
                f"**活跃用户数**: {total_users}",
                f"**平均消耗**: {avg_usage:.1f}",
                "",
                "📌 消耗排行榜 TOP 10",
                ""
            ]

            for idx, user_usage in enumerate(top_users, 1):
                lines.append(f"{idx}. **{user_usage.user_id}**: {user_usage.usage} 消耗")

            lines.append("")
            lines.append(f"**单用户限制**: {USAGE_LIMITS['user_daily_limit']}")
            lines.append(f"**超限用户数**: {len([u for u in user_usages if u.usage >= USAGE_LIMITS['user_daily_limit']])}")

            return chr(10).join(lines)

    except Exception as e:
        logger.error(f"❌ 获取消耗统计失败: {e}")
        return f"❌ 查询失败：{str(e)}"


@tool
def check_all_limits(
    user_id: str
) -> str:
    """
    综合检查全局和用户消耗限制（用于用户访问时快速检查）

    参数：
    - user_id: 用户ID

    返回：检查结果
    """
    try:
        with get_session() as session:
            # 检查是否为管理员
            user = session.query(UserAccount).filter_by(user_id=user_id).first()
            if user and user.is_admin:
                return f"""✅ 管理员账户，无任何限制

**用户ID**: {user_id}
**用户名**: {user.username}
"""

            today = date.today().strftime("%Y-%m-%d")

            # 1. 检查全局消耗
            global_usage = session.query(GlobalDailyUsage).filter_by(date=today).first()
            if not global_usage:
                global_usage = GlobalDailyUsage(
                    date=today,
                    total_usage=0,
                    updated_at=datetime.utcnow()
                )
                session.add(global_usage)
                session.commit()

            # 2. 检查用户消耗
            user_usage = session.query(UserDailyUsage).filter_by(user_id=user_id, date=today).first()
            if not user_usage:
                user_usage = UserDailyUsage(
                    user_id=user_id,
                    date=today,
                    usage=0,
                    updated_at=datetime.utcnow()
                )
                session.add(user_usage)
                session.commit()

            # 3. 检查是否超限
            global_limit = USAGE_LIMITS["global_daily_limit"]
            user_limit = USAGE_LIMITS["user_daily_limit"]

            if global_usage.total_usage >= global_limit:
                logger.warning(f"⚠️ 全局消耗已超限 | 用户: {user_id}")
                return f"""❌ 全局消耗已超限

**今日总消耗**: {global_usage.total_usage}
**消耗限制**: {global_limit}
**提示**: 当日访问已超限，请明天再来
"""

            if user_usage.usage >= user_limit:
                logger.warning(f"⚠️ 用户消耗已超限 | 用户: {user_id}")
                return f"""❌ 用户消耗已超限

**用户ID**: {user_id}
**今日消耗**: {user_usage.usage}
**消耗限制**: {user_limit}
**提示**: 当日访问已超限，请明天再来
"""

            # 未超限，返回状态
            return f"""✅ 访问正常

**用户ID**: {user_id}
**用户今日消耗**: {user_usage.usage}/{user_limit}
**全局今日消耗**: {global_usage.total_usage}/{global_limit}
**状态**: 可以正常访问
"""


    except Exception as e:
        logger.error(f"❌ 检查消耗限制失败: {e}")
        return f"❌ 检查失败：{str(e)}"
