"""
邀请码管理工具
提供邀请码生成、验证、使用等功能
"""
import logging
import secrets
from datetime import datetime
from typing import Optional
from langchain.tools import tool

from storage.database.db import get_session
from storage.database.shared.model import InvitationCode, UserAccount

logger = logging.getLogger(__name__)


@tool
def generate_invitation_code(
    admin_user_id: str,
    count: int = 1,
    expires_days: Optional[int] = None
) -> str:
    """
    生成邀请码（仅管理员可调用）

    参数：
    - admin_user_id: 管理员用户ID
    - count: 生成数量（默认1）
    - expires_days: 有效期天数（可选，不设置则永久有效）

    返回：生成结果
    """
    try:
        # 验证是否为管理员
        with get_session() as session:
            admin = session.query(UserAccount).filter_by(user_id=admin_user_id).first()
            if not admin or not admin.is_admin:
                return "❌ 权限不足：只有管理员可以生成邀请码"

            generated_codes = []
            for _ in range(count):
                # 生成8位随机邀请码
                code = secrets.token_hex(4).upper()

                # 计算过期时间
                expires_at = None
                if expires_days:
                    from datetime import timedelta
                    expires_at = datetime.utcnow() + timedelta(days=expires_days)

                invitation = InvitationCode(
                    code=code,
                    is_used=False,
                    created_by=admin_user_id,
                    created_at=datetime.utcnow(),
                    expires_at=expires_at
                )
                session.add(invitation)
                generated_codes.append(code)

            session.commit()
            logger.info(f"✅ 管理员 {admin_user_id} 生成了 {count} 个邀请码")

            result = f"""✅ 邀请码生成成功！

**生成数量**: {count}
**生成者**: {admin_user_id}
{'**有效期**: 永久' if not expires_days else f'**有效期**: {expires_days} 天'}
**邀请码列表**:
{chr(10).join([f'  - {code}' for code in generated_codes])}
"""
            return result

    except Exception as e:
        logger.error(f"❌ 生成邀请码失败: {e}")
        return f"❌ 生成失败：{str(e)}"


@tool
def verify_invitation_code(
    code: str
) -> str:
    """
    验证邀请码是否有效

    参数：
    - code: 邀请码

    返回：验证结果
    """
    try:
        with get_session() as session:
            invitation = session.query(InvitationCode).filter_by(code=code.upper()).first()

            if not invitation:
                return """❌ 邀请码验证失败

**错误**: 邀请码不存在
"""

            if invitation.is_used:
                return f"""❌ 邀请码验证失败

**错误**: 邀请码已被使用
**使用时间**: {invitation.used_at}
**使用者**: {invitation.used_by_user_id}
"""

            if invitation.expires_at and invitation.expires_at < datetime.utcnow():
                return f"""❌ 邀请码验证失败

**错误**: 邀请码已过期
**过期时间**: {invitation.expires_at}
"""

            return f"""✅ 邀请码验证成功

**邀请码**: {invitation.code}
**创建者**: {invitation.created_by}
**创建时间**: {invitation.created_at}
{'**过期时间**: 永久有效' if not invitation.expires_at else f'**过期时间**: {invitation.expires_at}'}
"""

    except Exception as e:
        logger.error(f"❌ 验证邀请码失败: {e}")
        return f"❌ 验证失败：{str(e)}"


@tool
def use_invitation_code(
    code: str,
    user_id: str
) -> str:
    """
    使用邀请码进行注册

    参数：
    - code: 邀请码
    - user_id: 用户ID

    返回：使用结果
    """
    try:
        with get_session() as session:
            invitation = session.query(InvitationCode).filter_by(code=code.upper()).first()

            if not invitation:
                return """❌ 注册失败

**错误**: 邀请码不存在
"""

            if invitation.is_used:
                return f"""❌ 注册失败

**错误**: 邀请码已被使用
**使用者**: {invitation.used_by_user_id}
**使用时间**: {invitation.used_at}
"""

            if invitation.expires_at and invitation.expires_at < datetime.utcnow():
                return f"""❌ 注册失败

**错误**: 邀请码已过期
**过期时间**: {invitation.expires_at}
"""

            # 标记邀请码为已使用
            invitation.is_used = True
            invitation.used_by_user_id = user_id
            invitation.used_at = datetime.utcnow()

            session.commit()
            logger.info(f"✅ 用户 {user_id} 使用邀请码 {code} 注册成功")

            return f"""✅ 注册成功！

**用户ID**: {user_id}
**邀请码**: {code}
**使用时间**: {datetime.utcnow()}
"""


    except Exception as e:
        logger.error(f"❌ 使用邀请码失败: {e}")
        return f"❌ 注册失败：{str(e)}"


@tool
def list_invitation_codes(
    admin_user_id: str,
    show_used: bool = False
) -> str:
    """
    列出所有邀请码（仅管理员可调用）

    参数：
    - admin_user_id: 管理员用户ID
    - show_used: 是否显示已使用的邀请码（默认False）

    返回：邀请码列表
    """
    try:
        # 验证是否为管理员
        with get_session() as session:
            admin = session.query(UserAccount).filter_by(user_id=admin_user_id).first()
            if not admin or not admin.is_admin:
                return "❌ 权限不足：只有管理员可以查看邀请码"

            # 查询邀请码
            query = session.query(InvitationCode)
            if not show_used:
                query = query.filter_by(is_used=False)

            invitations = query.order_by(InvitationCode.created_at.desc()).all()

            if not invitations:
                return """📋 邀请码列表

暂无邀请码
"""

            # 格式化输出
            lines = ["📋 邀请码列表", "", f"**总数**: {len(invitations)}", ""]
            for inv in invitations:
                status = "✅ 未使用" if not inv.is_used else f"❌ 已使用（{inv.used_by_user_id}）"
                lines.append(f"**{inv.code}** | {status}")
                lines.append(f"  创建者: {inv.created_by} | 创建时间: {inv.created_at}")
                if inv.expires_at:
                    lines.append(f"  过期时间: {inv.expires_at}")
                lines.append("")

            return chr(10).join(lines)

    except Exception as e:
        logger.error(f"❌ 列出邀请码失败: {e}")
        return f"❌ 查询失败：{str(e)}"


@tool
def check_user_admin(
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
"""

            if user.is_admin:
                return f"""✅ 管理员账户

**用户ID**: {user.user_id}
**用户名**: {user.username}
**最后登录**: {user.last_login_at}
"""

            return f"""❌ 普通用户

**用户ID**: {user.user_id}
**用户名**: {user.username}
"""

    except Exception as e:
        logger.error(f"❌ 检查管理员身份失败: {e}")
        return f"❌ 检查失败：{str(e)}"
