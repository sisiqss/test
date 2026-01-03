"""
花名册工具 - 用于管理用户及其社交关系信息
提供CRUD操作：增删改查
"""
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from langchain.tools import tool

from storage.database.db import get_session
from storage.database.shared.model import (
    UserProfile,
    RelationshipType,
    RelationshipLevel,
    UserConversationMemory,
    ConversationType,
    DailyReport
)

logger = logging.getLogger(__name__)


def _parse_relationship_type(rel_type: str) -> RelationshipType:
    """解析关系类型字符串为枚举"""
    rel_type = rel_type.lower().replace(" ", "_")
    rel_type_map = {
        "本人": RelationshipType.SELF,
        "自己": RelationshipType.SELF,
        "me": RelationshipType.SELF,
        "同事": RelationshipType.COLLEAGUE,
        "父母": RelationshipType.PARENT,
        "父亲": RelationshipType.PARENT,
        "母亲": RelationshipType.PARENT,
        "儿女": RelationshipType.CHILD,
        "儿子": RelationshipType.CHILD,
        "女儿": RelationshipType.CHILD,
        "朋友": RelationshipType.FRIEND,
        "其他": RelationshipType.OTHER,
        "其它": RelationshipType.OTHER,
    }
    return rel_type_map.get(rel_type, RelationshipType.OTHER)


def _parse_relationship_level(rel_level: str) -> Optional[RelationshipLevel]:
    """解析关系级别字符串为枚举"""
    if not rel_level or rel_level.strip() == "":
        return None

    rel_level = rel_level.strip()
    level_map = {
        "+2": RelationshipLevel.LEVEL_2_SUPERIOR,
        "+1": RelationshipLevel.LEVEL_1_SUPERIOR,
        "0": RelationshipLevel.SAME_LEVEL,
        "-1": RelationshipLevel.LEVEL_1_SUBORDINATE,
        "-2": RelationshipLevel.LEVEL_2_SUBORDINATE,
        "上级": RelationshipLevel.LEVEL_1_SUPERIOR,
        "上两级": RelationshipLevel.LEVEL_2_SUPERIOR,
        "下属": RelationshipLevel.LEVEL_1_SUBORDINATE,
        "下两级": RelationshipLevel.LEVEL_2_SUBORDINATE,
        "平级": RelationshipLevel.SAME_LEVEL,
        "同级": RelationshipLevel.SAME_LEVEL,
    }
    return level_map.get(rel_level)


def _format_relationship_level(rel_level: Optional[RelationshipLevel]) -> str:
    """安全地格式化关系级别为字符串"""
    if rel_level is None:
        return ""
    if isinstance(rel_level, RelationshipLevel):
        return rel_level.value
    return str(rel_level)


@tool
def add_roster_entry(
    user_id: str,
    name: str,
    gender: str,
    relationship_type: str,
    current_location: str,
    birth_date: str = "",
    mbti: str = "",
    birth_place: str = "",
    relationship_level: str = "",
    company_name: str = "",
    company_type: str = "",
    job_title: str = "",
    job_level: str = "",
    notes: str = ""
) -> str:
    """
    添加花名册条目

    必填字段：
    - user_id: 用户ID
    - name: 姓名
    - gender: 性别（男/女）
    - relationship_type: 关系类型（本人/同事/父母/儿女/朋友/其他）
    - current_location: 现居地

    可选字段：
    - birth_date: 出生年月日时间（本人必须，其他人可选）
    - mbti: MBTI类型
    - birth_place: 出生地
    - relationship_level: 关系级别（仅同事需要，如：+1、0、-1）
    - company_name: 公司名称（职场信息，可缺省）
    - company_type: 公司类型（如：国企、私企、外企、互联网、金融等）
    - job_title: 职位类型（如：产品经理、工程师、运营等）
    - job_level: 职级（如：P6、P7、高级、经理等）
    - notes: 备注信息

    返回：添加结果
    """
    try:
        with get_session() as session:
            # 验证必填字段
            if not all([name, gender, relationship_type, current_location]):
                return "❌ 添加失败：姓名、性别、关系类型、现居地均为必填字段"

            # 如果是本人，验证出生日期
            rel_type = _parse_relationship_type(relationship_type)
            if rel_type == RelationshipType.SELF and not birth_date:
                return "❌ 添加失败：本人的出生年月日时间为必填字段"

            # 解析关系级别
            rel_level = None
            if relationship_level and rel_type == RelationshipType.COLLEAGUE:
                rel_level = _parse_relationship_level(relationship_level)

            # 创建花名册条目
            entry = UserProfile(
                user_id=user_id,
                name=name.strip(),
                gender=gender.strip(),
                relationship_type=rel_type,
                relationship_level=rel_level,
                birth_date=birth_date.strip() if birth_date else None,
                mbti=mbti.strip() if mbti else None,
                birth_place=birth_place.strip() if birth_place else None,
                current_location=current_location.strip(),
                company_name=company_name.strip() if company_name else None,
                company_type=company_type.strip() if company_type else None,
                job_title=job_title.strip() if job_title else None,
                job_level=job_level.strip() if job_level else None,
                notes=notes.strip() if notes else None,
            )

            session.add(entry)
            session.commit()
            session.refresh(entry)

            logger.info(f"✅ 成功添加花名册条目: {name} (ID: {entry.id})")

            return f"""✅ 添加成功！

**姓名**: {entry.name}
**关系**: {relationship_type} {' (' + relationship_level + ')' if relationship_level else ''}
**性别**: {entry.gender}
**现居地**: {entry.current_location}
{'**出生日期**: ' + entry.birth_date if entry.birth_date else ''}
{'**MBTI**: ' + entry.mbti if entry.mbti else ''}
{'**出生地**: ' + entry.birth_place if entry.birth_place else ''}
{'**公司名称**: ' + entry.company_name if entry.company_name else ''}
{'**公司类型**: ' + entry.company_type if entry.company_type else ''}
{'**职位类型**: ' + entry.job_title if entry.job_title else ''}
{'**职级**: ' + entry.job_level if entry.job_level else ''}
{'**备注**: ' + entry.notes if entry.notes else ''}
"""

    except Exception as e:
        logger.error(f"❌ 添加花名册条目失败: {e}")
        return f"❌ 添加失败：{str(e)}"


@tool
def get_roster_entries(user_id: str, relationship_type: str = "") -> str:
    """
    获取花名册列表

    参数：
    - user_id: 用户ID
    - relationship_type: 可选，按关系类型筛选（本人/同事/父母/儿女/朋友/其他）

    返回：花名册列表
    """
    try:
        with get_session() as session:
            query = session.query(UserProfile).filter(UserProfile.user_id == user_id)

            # 按关系类型筛选
            if relationship_type:
                rel_type = _parse_relationship_type(relationship_type)
                query = query.filter(UserProfile.relationship_type == rel_type)

            # 按创建时间倒序
            entries = query.order_by(UserProfile.created_at.desc()).all()

            if not entries:
                return "📋 花名册为空，还没有添加任何条目"

            # 格式化输出
            result = f"📋 **花名册**（共 {len(entries)} 条）\n\n"
            for entry in entries:
                rel_type_display = {
                    RelationshipType.SELF: "本人",
                    RelationshipType.COLLEAGUE: "同事",
                    RelationshipType.PARENT: "父母",
                    RelationshipType.CHILD: "儿女",
                    RelationshipType.FRIEND: "朋友",
                    RelationshipType.OTHER: "其他",
                }.get(entry.relationship_type, entry.relationship_type)

                rel_level_display = f" ({_format_relationship_level(entry.relationship_level)})"

                result += f"**{entry.name}** - {rel_type_display}{rel_level_display}\n"
                result += f"  性别: {entry.gender} | "
                result += f"现居地: {entry.current_location}\n"
                if entry.birth_date:
                    result += f"  出生日期: {entry.birth_date}\n"
                if entry.mbti:
                    result += f"  MBTI: {entry.mbti}\n"
                if entry.bazi:
                    result += f"  八字: {entry.bazi[:20]}...\n"  # 只显示前20个字符
                if entry.birth_place:
                    result += f"  出生地: {entry.birth_place}\n"
                if entry.company_name:
                    result += f"  公司名称: {entry.company_name}\n"
                if entry.company_type:
                    result += f"  公司类型: {entry.company_type}\n"
                if entry.job_title:
                    result += f"  职位: {entry.job_title}\n"
                if entry.job_level:
                    result += f"  职级: {entry.job_level}\n"
                if entry.notes:
                    result += f"  备注: {entry.notes}\n"
                result += f"  ID: {entry.id} | 更新时间: {entry.updated_at.strftime('%Y-%m-%d %H:%M')}\n"
                result += "\n"

            return result

    except Exception as e:
        logger.error(f"❌ 获取花名册失败: {e}")
        return f"❌ 获取失败：{str(e)}"


@tool
def get_roster_entry_by_id(entry_id: int) -> str:
    """
    根据ID获取花名册条目详情

    参数：
    - entry_id: 条目ID

    返回：条目详情
    """
    try:
        with get_session() as session:
            entry = session.query(UserProfile).filter(UserProfile.id == entry_id).first()

            if not entry:
                return f"❌ 未找到ID为 {entry_id} 的条目"

            rel_type_display = {
                RelationshipType.SELF: "本人",
                RelationshipType.COLLEAGUE: "同事",
                RelationshipType.PARENT: "父母",
                RelationshipType.CHILD: "儿女",
                RelationshipType.FRIEND: "朋友",
                RelationshipType.OTHER: "其他",
            }.get(entry.relationship_type, entry.relationship_type)

            rel_level_display = f" ({_format_relationship_level(entry.relationship_level)})"

            result = f"""📋 **花名册条目详情**

**ID**: {entry.id}
**姓名**: {entry.name}
**性别**: {entry.gender}
**关系**: {rel_type_display}{rel_level_display}
**现居地**: {entry.current_location}
{'**出生日期**: ' + entry.birth_date if entry.birth_date else ''}
{'**八字**: ' + entry.bazi if entry.bazi else ''}
{'**MBTI**: ' + entry.mbti if entry.mbti else ''}
{'**出生地**: ' + entry.birth_place if entry.birth_place else ''}
{'**公司名称**: ' + entry.company_name if entry.company_name else ''}
{'**公司类型**: ' + entry.company_type if entry.company_type else ''}
{'**职位类型**: ' + entry.job_title if entry.job_title else ''}
{'**职级**: ' + entry.job_level if entry.job_level else ''}
{'**备注**: ' + entry.notes if entry.notes else ''}
**创建时间**: {entry.created_at.strftime('%Y-%m-%d %H:%M:%S')}
**更新时间**: {entry.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
            return result

    except Exception as e:
        logger.error(f"❌ 获取花名册条目失败: {e}")
        return f"❌ 获取失败：{str(e)}"


@tool
def update_roster_entry(
    entry_id: int,
    name: str = "",
    gender: str = "",
    current_location: str = "",
    birth_date: str = "",
    mbti: str = "",
    birth_place: str = "",
    relationship_type: str = "",
    relationship_level: str = "",
    company_name: str = "",
    company_type: str = "",
    job_title: str = "",
    job_level: str = "",
    notes: str = ""
) -> str:
    """
    更新花名册条目

    参数：
    - entry_id: 条目ID（必须）
    - name: 姓名（可选）
    - gender: 性别（可选）
    - current_location: 现居地（可选）
    - birth_date: 出生日期（可选）
    - mbti: MBTI类型（可选）
    - birth_place: 出生地（可选）
    - relationship_type: 关系类型（可选）
    - relationship_level: 关系级别（可选）
    - company_name: 公司名称（可选）
    - company_type: 公司类型（可选）
    - job_title: 职位类型（可选）
    - job_level: 职级（可选）
    - notes: 备注（可选）

    返回：更新结果
    """
    try:
        with get_session() as session:
            entry = session.query(UserProfile).filter(UserProfile.id == entry_id).first()

            if not entry:
                return f"❌ 未找到ID为 {entry_id} 的条目"

            # 更新提供的字段
            updated_fields = []
            if name:
                entry.name = name.strip()
                updated_fields.append("姓名")
            if gender:
                entry.gender = gender.strip()
                updated_fields.append("性别")
            if current_location:
                entry.current_location = current_location.strip()
                updated_fields.append("现居地")
            if birth_date:
                entry.birth_date = birth_date.strip()
                updated_fields.append("出生日期")
            if mbti:
                entry.mbti = mbti.strip()
                updated_fields.append("MBTI")
            if birth_place:
                entry.birth_place = birth_place.strip()
                updated_fields.append("出生地")
            if relationship_type:
                rel_type = _parse_relationship_type(relationship_type)
                entry.relationship_type = rel_type
                updated_fields.append("关系类型")
            if relationship_level and entry.relationship_type == RelationshipType.COLLEAGUE:
                rel_level = _parse_relationship_level(relationship_level)
                entry.relationship_level = rel_level
                updated_fields.append("关系级别")
            if company_name:
                entry.company_name = company_name.strip()
                updated_fields.append("公司名称")
            if company_type:
                entry.company_type = company_type.strip()
                updated_fields.append("公司类型")
            if job_title:
                entry.job_title = job_title.strip()
                updated_fields.append("职位类型")
            if job_level:
                entry.job_level = job_level.strip()
                updated_fields.append("职级")
            if notes:
                entry.notes = notes.strip()
                updated_fields.append("备注")

            entry.updated_at = datetime.utcnow()
            session.commit()

            logger.info(f"✅ 成功更新花名册条目: {entry.name} (ID: {entry.id})")

            return f"""✅ 更新成功！

**更新了以下字段**: {', '.join(updated_fields)}

**姓名**: {entry.name}
**关系**: {entry.relationship_type} {' (' + _format_relationship_level(entry.relationship_level) + ')' if _format_relationship_level(entry.relationship_level) else ''}
**性别**: {entry.gender}
**现居地**: {entry.current_location}
{'**出生日期**: ' + entry.birth_date if entry.birth_date else ''}
{'**MBTI**: ' + entry.mbti if entry.mbti else ''}
{'**出生地**: ' + entry.birth_place if entry.birth_place else ''}
{'**公司名称**: ' + entry.company_name if entry.company_name else ''}
{'**公司类型**: ' + entry.company_type if entry.company_type else ''}
{'**职位类型**: ' + entry.job_title if entry.job_title else ''}
{'**职级**: ' + entry.job_level if entry.job_level else ''}
"""

    except Exception as e:
        logger.error(f"❌ 更新花名册条目失败: {e}")
        return f"❌ 更新失败：{str(e)}"


@tool
def delete_roster_entry(entry_id: int) -> str:
    """
    删除花名册条目

    参数：
    - entry_id: 条目ID

    返回：删除结果
    """
    try:
        with get_session() as session:
            entry = session.query(UserProfile).filter(UserProfile.id == entry_id).first()

            if not entry:
                return f"❌ 未找到ID为 {entry_id} 的条目"

            entry_name = entry.name
            session.delete(entry)
            session.commit()

            logger.info(f"✅ 成功删除花名册条目: {entry_name} (ID: {entry_id})")

            return f"✅ 删除成功！已删除条目：{entry_name}"

    except Exception as e:
        logger.error(f"❌ 删除花名册条目失败: {e}")
        return f"❌ 删除失败：{str(e)}"


@tool
def search_roster_entries(user_id: str, keyword: str) -> str:
    """
    搜索花名册条目

    参数：
    - user_id: 用户ID
    - keyword: 搜索关键词（姓名、MBTI、备注等）

    返回：匹配的条目列表
    """
    try:
        with get_session() as session:
            keyword = keyword.strip()

            # 搜索姓名、MBTI、备注
            query = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                (UserProfile.name.ilike(f"%{keyword}%") |
                 UserProfile.mbti.ilike(f"%{keyword}%") |
                 UserProfile.notes.ilike(f"%{keyword}%"))
            )

            entries = query.order_by(UserProfile.created_at.desc()).all()

            if not entries:
                return f"🔍 未找到包含关键词 '{keyword}' 的条目"

            # 格式化输出
            result = f"🔍 **搜索结果**（关键词: '{keyword}'，共 {len(entries)} 条）\n\n"
            for entry in entries:
                result += f"**{entry.name}** (ID: {entry.id})\n"
                if entry.mbti:
                    result += f"  MBTI: {entry.mbti}\n"
                if entry.notes:
                    result += f"  备注: {entry.notes[:50]}...\n"
                result += "\n"

            return result

    except Exception as e:
        logger.error(f"❌ 搜索花名册失败: {e}")
        return f"❌ 搜索失败：{str(e)}"


@tool
def add_user_bazi(user_id: str, bazi: str) -> str:
    """
    为用户添加八字信息（系统产出）

    参数：
    - user_id: 用户ID
    - bazi: 八字信息

    返回：添加结果
    """
    try:
        with get_session() as session:
            # 查找本人的条目
            entry = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.relationship_type == RelationshipType.SELF
            ).first()

            if not entry:
                return "❌ 未找到本人的信息，请先添加本人信息到花名册"

            entry.bazi = bazi.strip()
            entry.updated_at = datetime.utcnow()
            session.commit()

            logger.info(f"✅ 成功为用户 {entry.name} 添加八字信息")

            return f"✅ 成功为 {entry.name} 添加八字信息！"

    except Exception as e:
        logger.error(f"❌ 添加八字信息失败: {e}")
        return f"❌ 添加失败：{str(e)}"


@tool
def save_life_interpretation(user_id: str, interpretation: dict) -> str:
    """
    保存用户的人生解读报告

    参数：
    - user_id: 用户ID
    - interpretation: 人生解读报告（字典格式），包含：
      - bazi_info: 八字排盘信息
      - five_elements: 五行分析
      - personality: 性格特点
      - fate_features: 命盘特点

    返回：保存结果
    """
    try:
        with get_session() as session:
            # 查找本人的条目
            entry = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.relationship_type == RelationshipType.SELF
            ).first()

            if not entry:
                return "❌ 未找到本人的信息，请先添加本人信息到花名册"

            entry.life_interpretation = interpretation
            entry.life_interpretation_generated_at = datetime.utcnow()
            entry.updated_at = datetime.utcnow()
            session.commit()

            logger.info(f"✅ 成功保存用户 {entry.name} 的人生解读报告")

            return f"✅ 成功保存 {entry.name} 的人生解读报告！"

    except Exception as e:
        logger.error(f"❌ 保存人生解读报告失败: {e}")
        return f"❌ 保存失败：{str(e)}"


@tool
def get_life_interpretation(user_id: str) -> str:
    """
    获取用户的人生解读报告

    参数：
    - user_id: 用户ID

    返回：人生解读报告内容
    """
    try:
        with get_session() as session:
            entry = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.relationship_type == RelationshipType.SELF
            ).first()

            if not entry:
                return "❌ 未找到本人的信息"

            if not entry.life_interpretation:
                return "📋 尚未生成人生解读报告，请先生成报告"

            interpretation = entry.life_interpretation

            # 格式化输出
            result = f"📚 **{entry.name} 的人生解读**\n\n"
            result += f"生成时间: {entry.life_interpretation_generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            result += "---\n\n"

            if interpretation.get("bazi_info"):
                result += "### 🎯 八字排盘\n"
                for key, value in interpretation["bazi_info"].items():
                    result += f"- **{key}**: {value}\n"
                result += "\n"

            if interpretation.get("five_elements"):
                result += "### 🌟 五行分析\n"
                for key, value in interpretation["five_elements"].items():
                    result += f"- **{key}**: {value}\n"
                result += "\n"

            if interpretation.get("personality"):
                result += "### 💡 性格特点\n"
                if isinstance(interpretation["personality"], list):
                    for trait in interpretation["personality"]:
                        result += f"- {trait}\n"
                else:
                    result += f"{interpretation['personality']}\n"
                result += "\n"

            if interpretation.get("fate_features"):
                result += "### 🎲 命盘特点\n"
                if isinstance(interpretation["fate_features"], list):
                    for feature in interpretation["fate_features"]:
                        result += f"- {feature}\n"
                else:
                    result += f"{interpretation['fate_features']}\n"
                result += "\n"

            return result

    except Exception as e:
        logger.error(f"❌ 获取人生解读报告失败: {e}")
        return f"❌ 获取失败：{str(e)}"


@tool
def save_career_trend(user_id: str, career_trend: dict) -> str:
    """
    保存用户的职场大势报告

    参数：
    - user_id: 用户ID
    - career_trend: 职场大势报告（字典格式），包含：
      - career_direction: 事业方向
      - wealth_limit: 财富上限
      - key_turning_points: 关键职业转折点
      - next_turning_point: 下一个转运点
      - career_trend_chart: 职场运势走势图数据

    返回：保存结果
    """
    try:
        with get_session() as session:
            # 查找本人的条目
            entry = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.relationship_type == RelationshipType.SELF
            ).first()

            if not entry:
                return "❌ 未找到本人的信息，请先添加本人信息到花名册"

            # 检查是否已录入职场信息
            if not entry.job_title or not entry.job_level:
                return "⚠️ 请先录入职场信息（职位类型、职级）后再生成职场大势报告"

            entry.career_trend = career_trend
            entry.career_trend_generated_at = datetime.utcnow()
            entry.updated_at = datetime.utcnow()
            session.commit()

            logger.info(f"✅ 成功保存用户 {entry.name} 的职场大势报告")

            return f"✅ 成功保存 {entry.name} 的职场大势报告！"

    except Exception as e:
        logger.error(f"❌ 保存职场大势报告失败: {e}")
        return f"❌ 保存失败：{str(e)}"


@tool
def get_career_trend(user_id: str) -> str:
    """
    获取用户的职场大势报告

    参数：
    - user_id: 用户ID

    返回：职场大势报告内容
    """
    try:
        with get_session() as session:
            entry = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.relationship_type == RelationshipType.SELF
            ).first()

            if not entry:
                return "❌ 未找到本人的信息"

            if not entry.career_trend:
                return "📋 尚未生成职场大势报告，请先生成报告"

            trend = entry.career_trend

            # 格式化输出
            result = f"💼 **{entry.name} 的职场大势**\n\n"
            result += f"生成时间: {entry.career_trend_generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            result += "---\n\n"

            if trend.get("career_direction"):
                result += "### 🎯 事业方向\n"
                result += f"{trend['career_direction']}\n\n"

            if trend.get("wealth_limit"):
                result += "### 💰 财富上限\n"
                result += f"{trend['wealth_limit']}\n\n"

            if trend.get("key_turning_points"):
                result += "### 🔄 关键职业转折点\n"
                if isinstance(trend["key_turning_points"], list):
                    for point in trend["key_turning_points"]:
                        result += f"- {point}\n"
                else:
                    result += f"{trend['key_turning_points']}\n"
                result += "\n"

            if trend.get("next_turning_point"):
                result += "### ⭐ 下一个转运点\n"
                result += f"{trend['next_turning_point']}\n\n"

            if trend.get("career_trend_chart"):
                result += "### 📈 职场运势走势图\n"
                result += "（走势图数据已保存，可生成可视化图表）\n\n"

            return result

    except Exception as e:
        logger.error(f"❌ 获取职场大势报告失败: {e}")
        return f"❌ 获取失败：{str(e)}"


@tool
def save_daily_report(user_id: str, report_date: str, report_data: dict) -> str:
    """
    保存每日报告（运势和穿搭）

    参数：
    - user_id: 用户ID
    - report_date: 报告日期（格式：YYYY-MM-DD）
    - report_data: 每日报告数据（字典格式），包含：
      - fortune_score: 运势指数（1-5）
      - fortune_yi: 今日宜事项（列表）
      - fortune_ji: 今日忌事项（列表）
      - fortune_mood: 今日心情
      - fortune_status: 今日状态
      - fortune_work_situation: 职场中可能发生的状况
      - fortune_advice: 给用户的建议
      - lucky_number: 幸运数字
      - lucky_color: 幸运色
      - weather: 今日天气
      - dressing_style: 穿搭风格建议
      - dressing_color: 配色建议
      - dressing_details: 具体穿搭推荐
      - dressing_image_url: 穿搭图片URL（可选）
      - fashion_trends: 流行趋势信息（可选）

    返回：保存结果
    """
    try:
        with get_session() as session:
            # 检查是否已存在当日报告
            existing_report = session.query(DailyReport).filter(
                DailyReport.user_id == user_id,
                DailyReport.report_date == report_date
            ).first()

            if existing_report:
                # 更新现有报告
                for key, value in report_data.items():
                    if hasattr(existing_report, key):
                        setattr(existing_report, key, value)
                session.commit()
                logger.info(f"✅ 成功更新用户 {report_date} 的每日报告")
                return f"✅ 成功更新 {report_date} 的每日报告！"

            # 创建新报告
            report = DailyReport(
                user_id=user_id,
                report_date=report_date,
                fortune_score=report_data.get("fortune_score"),
                fortune_yi=report_data.get("fortune_yi"),
                fortune_ji=report_data.get("fortune_ji"),
                fortune_mood=report_data.get("fortune_mood"),
                fortune_status=report_data.get("fortune_status"),
                fortune_work_situation=report_data.get("fortune_work_situation"),
                fortune_advice=report_data.get("fortune_advice"),
                lucky_number=report_data.get("lucky_number"),
                lucky_color=report_data.get("lucky_color"),
                weather=report_data.get("weather"),
                dressing_style=report_data.get("dressing_style"),
                dressing_color=report_data.get("dressing_color"),
                dressing_details=report_data.get("dressing_details"),
                dressing_image_url=report_data.get("dressing_image_url"),
                fashion_trends=report_data.get("fashion_trends"),
            )
            session.add(report)
            session.commit()

            logger.info(f"✅ 成功保存用户 {report_date} 的每日报告")

            return f"✅ 成功保存 {report_date} 的每日报告！"

    except Exception as e:
        logger.error(f"❌ 保存每日报告失败: {e}")
        return f"❌ 保存失败：{str(e)}"


@tool
def get_daily_report(user_id: str, report_date: str = "") -> str:
    """
    获取每日报告（运势和穿搭）

    参数：
    - user_id: 用户ID
    - report_date: 报告日期（格式：YYYY-MM-DD），不填则使用今天

    返回：每日报告内容
    """
    try:
        from datetime import date

        with get_session() as session:
            # 如果没有指定日期，使用今天
            if not report_date:
                report_date = date.today().strftime("%Y-%m-%d")

            report = session.query(DailyReport).filter(
                DailyReport.user_id == user_id,
                DailyReport.report_date == report_date
            ).first()

            if not report:
                return f"📋 尚未生成 {report_date} 的每日报告"

            # 格式化输出
            result = f"📅 **{report_date} 每日报告**\n\n"

            # 每日运势部分
            result += "✨ **今日运势**\n\n"
            if report.fortune_score:
                stars = "⭐" * report.fortune_score
                result += f"**运势指数**: {stars}\n\n"

            if report.fortune_yi:
                result += f"**今日宜**:\n"
                for item in report.fortune_yi:
                    result += f"- {item}\n"
                result += "\n"

            if report.fortune_ji:
                result += f"**今日忌**:\n"
                for item in report.fortune_ji:
                    result += f"- {item}\n"
                result += "\n"

            if report.fortune_mood:
                result += f"**今日心情**: {report.fortune_mood}\n\n"

            if report.fortune_status:
                result += f"**今日状态**: {report.fortune_status}\n\n"

            if report.fortune_work_situation:
                result += f"**职场可能发生**: {report.fortune_work_situation}\n\n"

            if report.fortune_advice:
                result += f"**建议**: {report.fortune_advice}\n\n"

            if report.lucky_number:
                result += f"**幸运数字**: {report.lucky_number}\n\n"

            if report.lucky_color:
                result += f"**幸运色**: {report.lucky_color}\n\n"

            result += "---\n\n"

            # 穿搭建议部分
            result += "👔 **穿搭建议**\n\n"

            if report.weather:
                result += f"**今日天气**: {report.weather}\n\n"

            if report.dressing_style:
                result += f"**穿搭风格**: {report.dressing_style}\n\n"

            if report.dressing_color:
                result += f"**配色建议**: {report.dressing_color}\n\n"

            if report.dressing_details:
                result += f"**具体穿搭**: {report.dressing_details}\n\n"

            if report.dressing_image_url:
                result += f"**穿搭图片**: [查看穿搭建议]({report.dressing_image_url})\n\n"

            if report.fashion_trends:
                result += f"**当前流行趋势**: 已收录最新流行元素\n\n"

            return result

    except Exception as e:
        logger.error(f"❌ 获取每日报告失败: {e}")
        return f"❌ 获取失败：{str(e)}"


@tool
def save_user_photo(user_id: str, photo_url: str) -> str:
    """
    保存用户照片（用于穿搭建议）

    参数：
    - user_id: 用户ID
    - photo_url: 照片URL

    返回：保存结果
    """
    try:
        with get_session() as session:
            # 查找本人的条目
            entry = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.relationship_type == RelationshipType.SELF
            ).first()

            if not entry:
                return "❌ 未找到本人的信息，请先添加本人信息到花名册"

            entry.photo_url = photo_url
            entry.updated_at = datetime.utcnow()
            session.commit()

            logger.info(f"✅ 成功保存用户 {entry.name} 的照片")

            return f"✅ 成功保存照片！后续将基于您的照片生成个性化穿搭建议。"

    except Exception as e:
        logger.error(f"❌ 保存用户照片失败: {e}")
        return f"❌ 保存失败：{str(e)}"


@tool
def check_user_info_exists(user_id: str) -> str:
    """
    检查用户是否已录入本人信息

    参数：
    - user_id: 用户ID

    返回：检查结果（包含是否已录入、是否已完成职场信息录入等信息）
    """
    try:
        with get_session() as session:
            entry = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.relationship_type == RelationshipType.SELF
            ).first()

            if not entry:
                return json.dumps({
                    "has_basic_info": False,
                    "has_work_info": False,
                    "message": "用户尚未录入本人信息"
                }, ensure_ascii=False)

            has_work_info = bool(entry.job_title and entry.job_level)

            result = {
                "has_basic_info": True,
                "has_work_info": has_work_info,
                "user_name": entry.name,
                "message": "用户已录入本人信息" + ("，且已完成职场信息录入" if has_work_info else "，但尚未录入职场信息")
            }

            return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"❌ 检查用户信息失败: {e}")
        return f"❌ 检查失败：{str(e)}"
