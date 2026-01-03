from sqlalchemy import BigInteger, DateTime, Identity, Index, Integer, JSON, Text, String, Enum as SQLEnum
from typing import Optional
import datetime
from enum import Enum

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

# 关系类型枚举
class RelationshipType(str, Enum):
    SELF = "self"  # 本人
    COLLEAGUE = "colleague"  # 同事
    PARENT = "parent"  # 父母
    CHILD = "child"  # 儿女
    FRIEND = "friend"  # 朋友
    OTHER = "other"  # 其他

# 同事关系级别枚举（仅用于COLLEAGUE类型）
class RelationshipLevel(str, Enum):
    LEVEL_2_SUPERIOR = "+2"  # 上两级（领导的领导）
    LEVEL_1_SUPERIOR = "+1"  # 上一级（直接领导）
    SAME_LEVEL = "0"  # 平级
    LEVEL_1_SUBORDINATE = "-1"  # 下一级（直接下属）
    LEVEL_2_SUBORDINATE = "-2"  # 下两级（下属的下属）

# 对话类型枚举
class ConversationType(str, Enum):
    PERSONAL_INFO = "personal_info"  # 个人信息相关
    WORKPLACE_ADVICE = "workplace_advice"  # 职场建议
    RELATIONSHIP_ADVICE = "relationship_advice"  # 人际关系建议
    CAREER_TRANSITION = "career_transition"  # 职业转型
    EMOTIONAL_SUPPORT = "emotional_support"  # 情绪支持
    FORTUNE_ANALYSIS = "fortune_analysis"  # 命理分析
    OTHER = "other"  # 其他


# 用户信息表（花名册）
class UserProfile(Base):
    """用户个人信息表，存储用户及其社交关系的信息"""
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True, comment="所属用户ID（使用Agent的用户）")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="姓名")
    gender: Mapped[str] = mapped_column(String(10), nullable=False, comment="性别：男/女")
    relationship_type: Mapped[str] = mapped_column(
        SQLEnum(RelationshipType),
        nullable=False,
        comment="关系类型：本人/同事/父母/儿女/朋友/其他"
    )
    relationship_level: Mapped[Optional[str]] = mapped_column(
        SQLEnum(RelationshipLevel),
        nullable=True,
        comment="关系级别（仅同事）：+2/+1/0/-1/-2"
    )
    birth_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="出生年月日时间")
    bazi: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="八字（系统产出）")
    mbti: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="MBTI类型")
    birth_place: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="出生地")
    current_location: Mapped[str] = mapped_column(String(255), nullable=False, comment="现居地")

    # 职场信息（可缺省，在用户查看职场相关信息时引导填写）
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="公司名称")
    company_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="公司类型（如：国企、私企、外企、互联网、金融等）")
    job_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="职位类型（如：产品经理、工程师、运营等）")
    job_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="职级（如：P6、P7、高级、经理等）")

    # 人生解读报告（生成后保存，后续直接读取）
    life_interpretation: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="人生解读报告（JSON格式，包含八字排盘、五行分析、性格特点、命盘特点等）")
    life_interpretation_generated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True, comment="人生解读报告生成时间")

    # 职场大势报告（生成后保存，后续直接读取）
    career_trend: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="职场大势报告（JSON格式，包含事业方向、财富上限、关键转折点、下一个转运点、职场运势走势图等）")
    career_trend_generated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True, comment="职场大势报告生成时间")

    # 用户照片（用于穿搭建议）
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="用户照片URL（用于穿搭建议生成）")

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="备注信息")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )

    __table_args__ = (
        Index("idx_user_id_name", "user_id", "name"),
        Index("idx_user_id_relationship", "user_id", "relationship_type"),
    )


# 用户沟通记忆表
class UserConversationMemory(Base):
    """用户与Agent沟通记忆表，存储重要对话信息"""
    __tablename__ = "user_conversation_memory"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True, comment="所属用户ID（使用Agent的用户）")
    contact_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="关联花名册中的联系人ID，为空表示与本人相关"
    )
    conversation_type: Mapped[str] = mapped_column(
        SQLEnum(ConversationType),
        nullable=False,
        comment="对话类型"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="对话内容摘要")
    important_info: Mapped[dict] = mapped_column(JSON, nullable=True, comment="重要信息提取（JSON格式）")
    sentiment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="情感倾向：positive/negative/neutral")
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, comment="标签列表")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )

    __table_args__ = (
        Index("idx_user_id_type", "user_id", "conversation_type"),
        Index("idx_user_id_contact", "user_id", "contact_user_id"),
        Index("idx_created_at", "created_at"),
    )


# 每日报告表（每日运势和穿搭建议）
class DailyReport(Base):
    """用户每日报告表，存储每日运势和穿搭建议"""
    __tablename__ = "daily_report"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True, comment="所属用户ID（使用Agent的用户）")
    report_date: Mapped[str] = mapped_column(String(20), index=True, comment="报告日期（格式：YYYY-MM-DD）")

    # 每日运势
    fortune_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="运势指数（1-5星）")
    fortune_yi: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, comment="今日宜事项")
    fortune_ji: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, comment="今日忌事项")
    fortune_mood: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="今日心情")
    fortune_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="今日状态")
    fortune_work_situation: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="职场中可能发生的状况")
    fortune_advice: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="给用户的建议")
    lucky_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="幸运数字")
    lucky_color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="幸运色")

    # 穿搭建议
    weather: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="今日天气")
    dressing_style: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="穿搭风格建议")
    dressing_color: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="配色建议（结合幸运色）")
    dressing_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="具体穿搭推荐")
    dressing_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="穿搭图片URL（基于用户照片生成）")

    # 流行趋势（从小红书等平台获取）
    fashion_trends: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="当前流行趋势信息")

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )

    __table_args__ = (
        Index("idx_daily_report_user_id_date", "user_id", "report_date"),
    )


# 用户账户表（用于账密认证）
class UserAccount(Base):
    """用户账户表，存储用户名、密码和管理员标识"""
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False, comment="用户ID（唯一标识）")
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="用户名")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False, comment="是否管理员")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    last_login_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True, comment="最后登录时间")

    __table_args__ = (
        Index("idx_username", "username"),
    )


# 用户每日消耗记录表
class UserDailyUsage(Base):
    """用户每日消耗记录表，跟踪单用户的每日消耗"""
    __tablename__ = "user_daily_usage"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, comment="用户ID")
    date: Mapped[str] = mapped_column(String(20), nullable=False, comment="日期（格式：YYYY-MM-DD）")
    usage: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="当日消耗")
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )

    __table_args__ = (
        Index("idx_user_id_date", "user_id", "date"),
    )


# 全局每日消耗记录表
class GlobalDailyUsage(Base):
    """全局每日消耗记录表，跟踪所有用户的每日总消耗"""
    __tablename__ = "global_daily_usage"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    date: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment="日期（格式：YYYY-MM-DD）")
    total_usage: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="当日总消耗")
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )

    __table_args__ = (
        Index("idx_date", "date"),
    )