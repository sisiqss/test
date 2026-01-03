"""
认证工具
提供用户登录、注册、管理员验证等功能
"""
import logging
import hashlib
from typing import Optional
from datetime import datetime
from langchain.tools import tool

from storage.database.db import get_session
from storage.database.shared.model import UserAccount

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    """使用SHA256哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()


@tool
def login(
    username: str,
    password: str
) -> str:
    """
    用户登录验证

    参数：
    - username: 用户名
    - password: 密码

    返回：登录结果（JSON格式）
    {
        "status": "success" | "failed",
        "message": "提示信息",
        "user_id": "用户ID",
        "username": "用户名",
        "is_admin": true/false,
        "login_time": "登录时间"
    }
    """
    try:
        with get_session() as session:
            # 查找用户
            user = session.query(UserAccount).filter_by(username=username).first()

            # 验证密码
            if not user:
                logger.warning(f"登录失败：用户不存在 | 用户名: {username}")
                return f"""❌ 登录失败：用户名或密码错误

**错误原因**: 用户名不存在
**输入的用户名**: {username}
**提示**: 请检查用户名是否正确，或联系管理员创建账户
"""

            # 检查密码
            password_hash = _hash_password(password)
            if user.password_hash != password_hash:
                logger.warning(f"登录失败：密码错误 | 用户名: {username}")
                return f"""❌ 登录失败：用户名或密码错误

**错误原因**: 密码错误
**用户名**: {username}
**提示**: 请检查密码是否正确，注意大小写
"""

            # 登录成功，更新最后登录时间
            user.last_login_at = datetime.utcnow()
            session.commit()

            logger.info(f"✅ 登录成功 | 用户名: {username} | 用户ID: {user.user_id} | 管理员: {user.is_admin}")

            # 返回成功信息（JSON格式，方便前端解析）
            return f"""✅ 登录成功

**用户ID**: {user.user_id}
**用户名**: {user.username}
**是否管理员**: {"是" if user.is_admin else "否"}
**登录时间**: {user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")}
**状态**: 成功
"""

    except Exception as e:
        logger.error(f"❌ 登录失败（异常）: {e}")
        return f"""❌ 登录失败：系统错误

**错误信息**: {str(e)}
**提示**: 请稍后重试，或联系管理员
"""


@tool
def register(
    user_id: str,
    username: str,
    password: str,
    is_admin: bool = False
) -> str:
    """
    用户注册（创建新账户）

    参数：
    - user_id: 用户ID（唯一标识，建议使用手机号或邮箱）
    - username: 用户名（用于登录）
    - password: 密码
    - is_admin: 是否为管理员（默认false）

    返回：注册结果
    """
    try:
        # 参数验证
        if not user_id or not username or not password:
            return """❌ 注册失败：参数不完整

**错误**: 用户ID、用户名和密码不能为空
"""

        if len(password) < 6:
            return """❌ 注册失败：密码长度不足

**错误**: 密码长度至少为6位
"""

        with get_session() as session:
            # 检查 user_id 是否已存在
            existing_user_id = session.query(UserAccount).filter_by(user_id=user_id).first()
            if existing_user_id:
                logger.warning(f"注册失败：user_id已存在 | user_id: {user_id}")
                return f"""❌ 注册失败：用户ID已存在

**错误原因**: user_id '{user_id}' 已被使用
**提示**: 请使用其他 user_id
"""

            # 检查 username 是否已存在
            existing_username = session.query(UserAccount).filter_by(username=username).first()
            if existing_username:
                logger.warning(f"注册失败：用户名已存在 | 用户名: {username}")
                return f"""❌ 注册失败：用户名已存在

**错误原因**: 用户名 '{username}' 已被使用
**提示**: 请使用其他用户名
"""

            # 创建新用户
            password_hash = _hash_password(password)
            new_user = UserAccount(
                user_id=user_id,
                username=username,
                password_hash=password_hash,
                is_admin=is_admin,
                created_at=datetime.utcnow()
            )

            session.add(new_user)
            session.commit()

            logger.info(f"✅ 注册成功 | user_id: {user_id} | username: {username} | is_admin: {is_admin}")

            return f"""✅ 注册成功

**用户ID**: {user_id}
**用户名**: {username}
**是否管理员**: {"是" if is_admin else "否"}
**创建时间**: {new_user.created_at.strftime("%Y-%m-%d %H:%M:%S")}
**提示**: 账户创建成功，请使用用户名和密码登录
"""

    except Exception as e:
        logger.error(f"❌ 注册失败（异常）: {e}")
        return f"""❌ 注册失败：系统错误

**错误信息**: {str(e)}
**提示**: 请稍后重试，或联系管理员
"""


@tool
def check_admin(
    user_id: str
) -> str:
    """
    检查用户是否为管理员

    参数：
    - user_id: 用户ID

    返回：检查结果
    """
    try:
        with get_session() as session:
            user = session.query(UserAccount).filter_by(user_id=user_id).first()

            if not user:
                return f"""❌ 用户不存在

**用户ID**: {user_id}
**提示**: 用户ID不存在，请检查是否正确
"""

            if user.is_admin:
                logger.info(f"✅ 管理员验证通过 | user_id: {user_id}")
                return f"""✅ 该用户是管理员

**用户ID**: {user_id}
**用户名**: {user.username}
**权限级别**: 管理员
**创建时间**: {user.created_at.strftime("%Y-%m-%d %H:%M:%S")}
"""
            else:
                logger.info(f"ℹ️ 普通用户 | user_id: {user_id}")
                return f"""ℹ️ 该用户是普通用户

**用户ID**: {user_id}
**用户名**: {user.username}
**权限级别**: 普通用户
**创建时间**: {user.created_at.strftime("%Y-%m-%d %H:%M:%S")}
"""

    except Exception as e:
        logger.error(f"❌ 检查管理员失败: {e}")
        return f"""❌ 检查失败：系统错误

**错误信息**: {str(e)}
"""


@tool
def get_user_info(
    user_id: str
) -> str:
    """
    获取用户信息

    参数：
    - user_id: 用户ID

    返回：用户信息
    """
    try:
        with get_session() as session:
            user = session.query(UserAccount).filter_by(user_id=user_id).first()

            if not user:
                return f"""❌ 用户不存在

**用户ID**: {user_id}
"""

            return f"""✅ 用户信息

**用户ID**: {user.user_id}
**用户名**: {user.username}
**是否管理员**: {"是" if user.is_admin else "否"}
**注册时间**: {user.created_at.strftime("%Y-%m-%d %H:%M:%S")}
**最后登录**: {user.last_login_at.strftime("%Y-%m-%d %H:%M:%S") if user.last_login_at else "从未登录"}
"""

    except Exception as e:
        logger.error(f"❌ 获取用户信息失败: {e}")
        return f"""❌ 查询失败：系统错误

**错误信息**: {str(e)}
"""


@tool
def reset_password(
    username: str,
    old_password: str,
    new_password: str
) -> str:
    """
    重置用户密码

    参数：
    - username: 用户名
    - old_password: 旧密码
    - new_password: 新密码

    返回：重置结果
    """
    try:
        # 参数验证
        if len(new_password) < 6:
            return """❌ 重置失败：新密码长度不足

**错误**: 新密码长度至少为6位
"""

        with get_session() as session:
            # 查找用户
            user = session.query(UserAccount).filter_by(username=username).first()

            if not user:
                return f"""❌ 重置失败：用户不存在

**用户名**: {username}
**提示**: 请检查用户名是否正确
"""

            # 验证旧密码
            old_password_hash = _hash_password(old_password)
            if user.password_hash != old_password_hash:
                return f"""❌ 重置失败：旧密码错误

**提示**: 旧密码不正确，请重新输入
"""

            # 更新密码
            user.password_hash = _hash_password(new_password)
            session.commit()

            logger.info(f"✅ 密码重置成功 | 用户名: {username}")

            return f"""✅ 密码重置成功

**用户名**: {username}
**更新时间**: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
**提示**: 请使用新密码登录
"""

    except Exception as e:
        logger.error(f"❌ 密码重置失败: {e}")
        return f"""❌ 重置失败：系统错误

**错误信息**: {str(e)}
"""
