"""
通用数据库操作工具
提供前端直接读写数据库的通用接口
"""
import logging
import json
from typing import Optional, Dict, List, Any
from datetime import datetime
from langchain.tools import tool

from storage.database.db import get_session
from storage.database.shared.model import (
    UserProfile,
    UserAccount,
    DailyReport,
    UserConversationMemory,
    UserDailyUsage,
    GlobalDailyUsage
)

logger = logging.getLogger(__name__)


@tool
def query_user_by_id(
    user_id: str
) -> str:
    """
    根据用户ID查询用户信息（对应 users 表）

    参数：
    - user_id: 用户ID

    返回：用户信息（JSON格式）
    """
    try:
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

            logger.info(f"✅ 查询用户成功 | user_id: {user_id}")
            return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ 查询用户失败: {e}")
        return f'{{"status": "failed", "error": "{str(e)}"}}'


@tool
def query_contacts(
    user_id: str,
    contact_type: Optional[str] = None
) -> str:
    """
    查询联系人列表（对应 contacts 表）

    参数：
    - user_id: 用户ID
    - contact_type: 联系人类型（可选：self/colleague/parent/child/friend/other）

    返回：联系人列表（JSON格式）
    """
    try:
        with get_session() as session:
            query = session.query(UserProfile).filter_by(user_id=user_id)

            # 过滤类型（排除本人）
            if contact_type:
                query = query.filter_by(relationship_type=contact_type)
            else:
                query = query.filter(UserProfile.relationship_type != "self")

            contacts = query.all()

            result = {
                "status": "success",
                "user_id": user_id,
                "total": len(contacts),
                "contacts": []
            }

            for contact in contacts:
                result["contacts"].append({
                    "id": contact.id,
                    "name": contact.name,
                    "gender": contact.gender,
                    "relationship_type": contact.relationship_type,
                    "relationship_level": contact.relationship_level,
                    "birth_date": contact.birth_date,
                    "bazi": contact.bazi,
                    "mbti": contact.mbti,
                    "birth_place": contact.birth_place,
                    "current_location": contact.current_location,
                    "company_name": contact.company_name,
                    "company_type": contact.company_type,
                    "job_title": contact.job_title,
                    "job_level": contact.job_level,
                    "notes": contact.notes,
                    "created_at": contact.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })

            logger.info(f"✅ 查询联系人成功 | user_id: {user_id} | 数量: {len(contacts)}")
            return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ 查询联系人失败: {e}")
        return f'{{"status": "failed", "error": "{str(e)}"}}'


@tool
def query_user_reports(
    user_id: str,
    report_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    查询用户报告（对应 user_reports 表）

    参数：
    - user_id: 用户ID
    - report_type: 报告类型（可选：daily/life/career）
    - start_date: 开始日期（格式：YYYY-MM-DD，仅daily类型有效）
    - end_date: 结束日期（格式：YYYY-MM-DD，仅daily类型有效）

    返回：报告数据（JSON格式）
    """
    try:
        with get_session() as session:
            result = {
                "status": "success",
                "user_id": user_id,
                "reports": {}
            }

            # 1. 查询用户档案中的报告
            profile = session.query(UserProfile).filter_by(
                user_id=user_id,
                relationship_type="self"
            ).first()

            if profile:
                if report_type in [None, "life"]:
                    if profile.life_interpretation:
                        result["reports"]["life"] = {
                            "generated_at": profile.life_interpretation_generated_at.strftime("%Y-%m-%d %H:%M:%S") if profile.life_interpretation_generated_at else None,
                            "data": profile.life_interpretation
                        }

                if report_type in [None, "career"]:
                    if profile.career_trend:
                        result["reports"]["career"] = {
                            "generated_at": profile.career_trend_generated_at.strftime("%Y-%m-%d %H:%M:%S") if profile.career_trend_generated_at else None,
                            "data": profile.career_trend
                        }

            # 2. 查询每日报告
            if report_type in [None, "daily"]:
                query = session.query(DailyReport).filter_by(user_id=user_id)

                if start_date:
                    query = query.filter(DailyReport.report_date >= start_date)
                if end_date:
                    query = query.filter(DailyReport.report_date <= end_date)

                daily_reports = query.order_by(DailyReport.report_date.desc()).limit(30).all()

                result["reports"]["daily"] = [
                    {
                        "id": report.id,
                        "report_date": report.report_date,
                        "fortune_score": report.fortune_score,
                        "fortune_yi": report.fortune_yi,
                        "fortune_ji": report.fortune_ji,
                        "fortune_mood": report.fortune_mood,
                        "fortune_status": report.fortune_status,
                        "fortune_work_situation": report.fortune_work_situation,
                        "fortune_advice": report.fortune_advice,
                        "lucky_number": report.lucky_number,
                        "lucky_color": report.lucky_color,
                        "weather": report.weather,
                        "dressing_style": report.dressing_style,
                        "dressing_color": report.dressing_color,
                        "dressing_details": report.dressing_details,
                        "dressing_image_url": report.dressing_image_url,
                        "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    for report in daily_reports
                ]

            logger.info(f"✅ 查询报告成功 | user_id: {user_id} | 类型: {report_type}")
            return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ 查询报告失败: {e}")
        return f'{{"status": "failed", "error": "{str(e)}"}}'


@tool
def update_user_profile(
    user_id: str,
    profile_data: str
) -> str:
    """
    更新用户档案信息（对应 users 表）

    参数：
    - user_id: 用户ID
    - profile_data: 档案数据（JSON字符串）

    返回：更新结果
    """
    try:
        data = json.loads(profile_data)

        with get_session() as session:
            # 查询用户档案（本人）
            profile = session.query(UserProfile).filter_by(
                user_id=user_id,
                relationship_type="self"
            ).first()

            if not profile:
                # 如果不存在，创建新的
                profile = UserProfile(
                    user_id=user_id,
                    name=data.get("name", ""),
                    gender=data.get("gender", "未知"),
                    relationship_type="self",
                    current_location=data.get("current_location", "")
                )
                session.add(profile)

            # 更新字段
            if "name" in data:
                profile.name = data["name"]
            if "gender" in data:
                profile.gender = data["gender"]
            if "birth_date" in data:
                profile.birth_date = data["birth_date"]
            if "mbti" in data:
                profile.mbti = data["mbti"]
            if "birth_place" in data:
                profile.birth_place = data["birth_place"]
            if "current_location" in data:
                profile.current_location = data["current_location"]
            if "company_name" in data:
                profile.company_name = data["company_name"]
            if "company_type" in data:
                profile.company_type = data["company_type"]
            if "job_title" in data:
                profile.job_title = data["job_title"]
            if "job_level" in data:
                profile.job_level = data["job_level"]
            if "photo_url" in data:
                profile.photo_url = data["photo_url"]
            if "notes" in data:
                profile.notes = data["notes"]

            profile.updated_at = datetime.utcnow()
            session.commit()

            logger.info(f"✅ 更新用户档案成功 | user_id: {user_id}")

            return f"""✅ 用户档案更新成功

**用户ID**: {user_id}
**姓名**: {profile.name}
**更新时间**: {profile.updated_at.strftime("%Y-%m-%d %H:%M:%S")}
"""

    except Exception as e:
        logger.error(f"❌ 更新用户档案失败: {e}")
        return f'{{"status": "failed", "error": "{str(e)}"}}'


@tool
def add_contact(
    user_id: str,
    contact_data: str
) -> str:
    """
    添加联系人（对应 contacts 表）

    参数：
    - user_id: 用户ID
    - contact_data: 联系人数据（JSON字符串）

    返回：添加结果
    """
    try:
        data = json.loads(contact_data)

        with get_session() as session:
            contact = UserProfile(
                user_id=user_id,
                name=data.get("name", ""),
                gender=data.get("gender", "未知"),
                relationship_type=data.get("relationship_type", "other"),
                relationship_level=data.get("relationship_level"),
                birth_date=data.get("birth_date"),
                bazi=data.get("bazi"),
                mbti=data.get("mbti"),
                birth_place=data.get("birth_place"),
                current_location=data.get("current_location", ""),
                company_name=data.get("company_name"),
                company_type=data.get("company_type"),
                job_title=data.get("job_title"),
                job_level=data.get("job_level"),
                notes=data.get("notes"),
                created_at=datetime.utcnow()
            )

            session.add(contact)
            session.commit()

            logger.info(f"✅ 添加联系人成功 | user_id: {user_id} | 姓名: {contact.name}")

            return f"""✅ 联系人添加成功

**联系人ID**: {contact.id}
**姓名**: {contact.name}
**关系类型**: {contact.relationship_type}
**创建时间**: {contact.created_at.strftime("%Y-%m-%d %H:%M:%S")}
"""

    except Exception as e:
        logger.error(f"❌ 添加联系人失败: {e}")
        return f'{{"status": "failed", "error": "{str(e)}"}}'


@tool
def save_report(
    user_id: str,
    report_type: str,
    report_data: str
) -> str:
    """
    保存报告（对应 user_reports 表）

    参数：
    - user_id: 用户ID
    - report_type: 报告类型（daily/life/career）
    - report_data: 报告数据（JSON字符串）

    返回：保存结果
    """
    try:
        data = json.loads(report_data)

        with get_session() as session:
            if report_type == "daily":
                # 保存每日报告
                report_date = data.get("report_date", datetime.utcnow().strftime("%Y-%m-%d"))

                # 检查是否已存在
                existing = session.query(DailyReport).filter_by(
                    user_id=user_id,
                    report_date=report_date
                ).first()

                if existing:
                    # 更新
                    existing.fortune_score = data.get("fortune_score")
                    existing.fortune_yi = data.get("fortune_yi")
                    existing.fortune_ji = data.get("fortune_ji")
                    existing.fortune_mood = data.get("fortune_mood")
                    existing.fortune_status = data.get("fortune_status")
                    existing.fortune_work_situation = data.get("fortune_work_situation")
                    existing.fortune_advice = data.get("fortune_advice")
                    existing.lucky_number = data.get("lucky_number")
                    existing.lucky_color = data.get("lucky_color")
                    existing.weather = data.get("weather")
                    existing.dressing_style = data.get("dressing_style")
                    existing.dressing_color = data.get("dressing_color")
                    existing.dressing_details = data.get("dressing_details")
                    existing.dressing_image_url = data.get("dressing_image_url")
                    existing.fashion_trends = data.get("fashion_trends")

                    session.commit()
                    msg = f"✅ 每日报告更新成功（日期: {report_date}）"
                else:
                    # 新增
                    new_report = DailyReport(
                        user_id=user_id,
                        report_date=report_date,
                        fortune_score=data.get("fortune_score"),
                        fortune_yi=data.get("fortune_yi"),
                        fortune_ji=data.get("fortune_ji"),
                        fortune_mood=data.get("fortune_mood"),
                        fortune_status=data.get("fortune_status"),
                        fortune_work_situation=data.get("fortune_work_situation"),
                        fortune_advice=data.get("fortune_advice"),
                        lucky_number=data.get("lucky_number"),
                        lucky_color=data.get("lucky_color"),
                        weather=data.get("weather"),
                        dressing_style=data.get("dressing_style"),
                        dressing_color=data.get("dressing_color"),
                        dressing_details=data.get("dressing_details"),
                        dressing_image_url=data.get("dressing_image_url"),
                        fashion_trends=data.get("fashion_trends"),
                        created_at=datetime.utcnow()
                    )
                    session.add(new_report)
                    session.commit()
                    msg = f"✅ 每日报告创建成功（日期: {report_date}）"

            elif report_type == "life":
                # 保存人生解读
                profile = session.query(UserProfile).filter_by(
                    user_id=user_id,
                    relationship_type="self"
                ).first()

                if profile:
                    profile.life_interpretation = data
                    profile.life_interpretation_generated_at = datetime.utcnow()
                    session.commit()
                    msg = "✅ 人生解读报告保存成功"
                else:
                    msg = "❌ 用户档案不存在"

            elif report_type == "career":
                # 保存职场大势
                profile = session.query(UserProfile).filter_by(
                    user_id=user_id,
                    relationship_type="self"
                ).first()

                if profile:
                    profile.career_trend = data
                    profile.career_trend_generated_at = datetime.utcnow()
                    session.commit()
                    msg = "✅ 职场大势报告保存成功"
                else:
                    msg = "❌ 用户档案不存在"

            else:
                return f'{{"status": "failed", "error": "不支持的报告类型: {report_type}"}}'

            logger.info(f"✅ 保存报告成功 | user_id: {user_id} | 类型: {report_type}")
            return msg

    except Exception as e:
        logger.error(f"❌ 保存报告失败: {e}")
        return f'{{"status": "failed", "error": "{str(e)}"}}'
