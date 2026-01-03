"""
每日运势和穿搭合并工具
一次性返回运势和穿搭建议，便于前端调用
"""
import logging
from datetime import datetime, date
from typing import Optional
from langchain.tools import tool

from storage.database.db import get_session
from storage.database.shared.model import UserProfile, DailyReport

logger = logging.getLogger(__name__)


@tool
def get_daily_fortune_and_outfit(
    user_id: str,
    report_date: str = "",
    force_refresh: bool = False,
    runtime=None
) -> str:
    """
    获取每日运势和穿搭建议（合并功能）

    优先从缓存读取，如果缓存不存在或过期，则自动生成并保存

    参数：
    - user_id: 用户ID
    - report_date: 报告日期（格式：YYYY-MM-DD），不填则使用今天
    - force_refresh: 是否强制刷新（默认False，优先使用缓存）

    返回：运势+穿搭的完整报告
    """
    try:
        from tools.weather_tool import get_weather, dressing_advice
        from tools.external_api_tool import bazi_api_analysis

        # 如果没有指定日期，使用今天
        if not report_date:
            report_date = date.today().strftime("%Y-%m-%d")

        with get_session() as session:
            # 1. 获取用户信息
            user_profile = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.relationship_type == "self"
            ).first()

            if not user_profile:
                return "❌ 未找到您的个人信息，请先完成注册"

            # 2. 检查是否有缓存
            daily_report = session.query(DailyReport).filter(
                DailyReport.user_id == user_id,
                DailyReport.report_date == report_date
            ).first()

            # 判断是否需要重新生成
            need_generate = (
                force_refresh or  # 强制刷新
                not daily_report or  # 无缓存
                (daily_report.created_at and
                 (datetime.utcnow() - daily_report.created_at).days >= 1)  # 缓存超过1天
            )

            if not need_generate and daily_report:
                # 返回缓存数据
                return _format_daily_report(daily_report, user_profile, from_cache=True)

            # 3. 生成运势数据
            logger.info(f"🔮 开始为用户 {user_id} 生成 {report_date} 的运势数据")

            # 调用八字分析工具获取运势
            bazi_result = bazi_api_analysis(
                user_id=user_id,
                query_date=report_date,
                runtime=runtime
            )

            # 解析八字分析结果
            fortune_data = _parse_bazi_result(bazi_result)

            # 4. 获取天气信息
            weather_info = ""
            city = user_profile.current_location.split("市")[0] if user_profile.current_location else "北京"

            try:
                weather_result = get_weather(city=city, runtime=runtime)
                weather_info = weather_result
            except Exception as e:
                logger.warning(f"⚠️ 获取天气信息失败: {e}")
                weather_info = "天气信息获取失败，请手动查看"

            # 5. 生成穿搭建议
            dressing_info = ""
            try:
                # 提取幸运色
                lucky_color = fortune_data.get("lucky_color", "蓝色")

                # 获取行业信息
                industry = user_profile.company_type if user_profile.company_type else "通用"

                # 调用穿搭建议工具
                dressing_result = dressing_advice(
                    industry=industry,
                    weather=_extract_weather_desc(weather_info),
                    lucky_color=lucky_color,
                    runtime=runtime
                )
                dressing_info = dressing_result
            except Exception as e:
                logger.warning(f"⚠️ 生成穿搭建议失败: {e}")
                dressing_info = f"👔 穿搭建议\n\n主色调：{fortune_data.get('lucky_color', '蓝色')}\n建议穿着舒适得体的服装"

            # 6. 保存到数据库
            if daily_report:
                # 更新现有记录
                daily_report.fortune_score = fortune_data.get("fortune_score")
                daily_report.fortune_yi = fortune_data.get("fortune_yi")
                daily_report.fortune_ji = fortune_data.get("fortune_ji")
                daily_report.fortune_mood = fortune_data.get("fortune_mood")
                daily_report.fortune_status = fortune_data.get("fortune_status")
                daily_report.fortune_work_situation = fortune_data.get("fortune_work_situation")
                daily_report.fortune_advice = fortune_data.get("fortune_advice")
                daily_report.lucky_number = fortune_data.get("lucky_number")
                daily_report.lucky_color = fortune_data.get("lucky_color")
                daily_report.weather = weather_info
                daily_report.dressing_style = _extract_dressing_style(dressing_info)
                daily_report.dressing_color = f"主色调：{fortune_data.get('lucky_color', '蓝色')}"
                daily_report.dressing_details = dressing_info
                daily_report.created_at = datetime.utcnow()
            else:
                # 创建新记录
                daily_report = DailyReport(
                    user_id=user_id,
                    report_date=report_date,
                    fortune_score=fortune_data.get("fortune_score"),
                    fortune_yi=fortune_data.get("fortune_yi"),
                    fortune_ji=fortune_data.get("fortune_ji"),
                    fortune_mood=fortune_data.get("fortune_mood"),
                    fortune_status=fortune_data.get("fortune_status"),
                    fortune_work_situation=fortune_data.get("fortune_work_situation"),
                    fortune_advice=fortune_data.get("fortune_advice"),
                    lucky_number=fortune_data.get("lucky_number"),
                    lucky_color=fortune_data.get("lucky_color"),
                    weather=weather_info,
                    dressing_style=_extract_dressing_style(dressing_info),
                    dressing_color=f"主色调：{fortune_data.get('lucky_color', '蓝色')}",
                    dressing_details=dressing_info,
                    created_at=datetime.utcnow()
                )
                session.add(daily_report)

            session.commit()
            logger.info(f"✅ {report_date} 的每日报告生成并保存成功")

            # 7. 格式化返回
            return _format_daily_report(daily_report, user_profile, from_cache=False)

    except Exception as e:
        logger.error(f"❌ 获取每日运势和穿搭失败: {e}")
        return f"❌ 获取失败：{str(e)}"


def _parse_bazi_result(bazi_result: str) -> dict:
    """解析八字分析结果，提取运势信息"""
    fortune_data = {
        "fortune_score": 3,
        "fortune_yi": ["积极工作", "与人交流"],
        "fortune_ji": ["冲动决策"],
        "fortune_mood": "平和",
        "fortune_status": "正常",
        "fortune_work_situation": "工作顺利",
        "fortune_advice": "保持专注",
        "lucky_number": "7",
        "lucky_color": "蓝色"
    }

    # 尝试从结果中提取信息（简单实现）
    result_lower = bazi_result.lower()

    # 提取幸运色
    for color in ["红色", "蓝色", "黄色", "绿色", "黑色", "白色", "紫色", "橙色"]:
        if color in bazi_result:
            fortune_data["lucky_color"] = color
            break

    # 提取幸运数字
    for num in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        if f"{num}位幸运数字" in bazi_result or f"幸运数字{num}" in bazi_result:
            fortune_data["lucky_number"] = num
            break

    # 提取运势指数
    if "五颗星" in bazi_result or "⭐⭐⭐⭐⭐" in bazi_result:
        fortune_data["fortune_score"] = 5
    elif "四颗星" in bazi_result or "⭐⭐⭐⭐" in bazi_result:
        fortune_data["fortune_score"] = 4
    elif "三颗星" in bazi_result or "⭐⭐⭐" in bazi_result:
        fortune_data["fortune_score"] = 3
    elif "二颗星" in bazi_result or "⭐⭐" in bazi_result:
        fortune_data["fortune_score"] = 2
    elif "一颗星" in bazi_result or "⭐" in bazi_result:
        fortune_data["fortune_score"] = 1

    return fortune_data


def _extract_weather_desc(weather_info: str) -> str:
    """从天气信息中提取描述"""
    if "晴天" in weather_info or "晴" in weather_info:
        return "晴天"
    elif "雨" in weather_info:
        return "下雨"
    elif "雪" in weather_info:
        return "下雪"
    elif "阴" in weather_info:
        return "阴天"
    elif "多云" in weather_info:
        return "多云"
    else:
        return "多云"


def _extract_dressing_style(dressing_info: str) -> str:
    """从穿搭建议中提取风格"""
    if "商务" in dressing_info:
        return "商务休闲"
    elif "正式" in dressing_info:
        return "正式商务"
    elif "休闲" in dressing_info:
        return "休闲舒适"
    else:
        return "得体大方"


def _format_daily_report(daily_report: DailyReport, user_profile: UserProfile, from_cache: bool) -> str:
    """格式化每日报告"""
    result = f"📅 **{daily_report.report_date} 每日运势与穿搭**\n\n"

    if from_cache:
        result += "✨ *（来自缓存）*\n\n"

    # 每日运势部分
    result += "### ✨ 今日运势\n\n"

    if daily_report.fortune_score:
        stars = "⭐" * daily_report.fortune_score
        result += f"**运势指数**: {stars} ({daily_report.fortune_score}/5)\n\n"

    if daily_report.lucky_number:
        result += f"**幸运数字**: {daily_report.lucky_number}\n\n"

    if daily_report.lucky_color:
        result += f"**幸运色**: {daily_report.lucky_color}\n\n"

    result += "---\n\n"

    if daily_report.fortune_yi:
        result += "**📌 今日宜**\n"
        for item in daily_report.fortune_yi:
            result += f"- {item}\n"
        result += "\n"

    if daily_report.fortune_ji:
        result += "**⚠️ 今日忌**\n"
        for item in daily_report.fortune_ji:
            result += f"- {item}\n"
        result += "\n"

    if daily_report.fortune_mood:
        result += f"**今日心情**: {daily_report.fortune_mood}\n\n"

    if daily_report.fortune_status:
        result += f"**今日状态**: {daily_report.fortune_status}\n\n"

    if daily_report.fortune_work_situation:
        result += f"**职场可能发生**: {daily_report.fortune_work_situation}\n\n"

    if daily_report.fortune_advice:
        result += f"**💡 今日建议**: {daily_report.fortune_advice}\n\n"

    result += "---\n\n"

    # 穿搭建议部分
    result += "### 👔 穿搭建议\n\n"

    if daily_report.weather:
        result += f"**🌤️ 今日天气**\n{daily_report.weather}\n\n"

    if daily_report.dressing_style:
        result += f"**👗 穿搭风格**: {daily_report.dressing_style}\n\n"

    if daily_report.dressing_color:
        result += f"**🎨 配色建议**: {daily_report.dressing_color}\n\n"

    if daily_report.dressing_details:
        result += f"**📝 具体穿搭**\n{daily_report.dressing_details}\n\n"

    result += f"---\n\n*生成时间: {daily_report.created_at.strftime('%Y-%m-%d %H:%M:%S')}*"

    return result
