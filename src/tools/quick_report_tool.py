"""
快速报告生成工具
支持分步生成人生报告，优化响应速度
"""

from langchain.tools import tool
import json
from typing import Optional


@tool
def generate_quick_report(user_id: str) -> str:
    """
    快速生成人生报告，优先从数据库读取已保存的报告。
    
    如果数据库中已有完整报告，直接返回；否则生成精简版报告。
    
    Args:
        user_id: 用户ID
        
    Returns:
        JSON格式的报告数据，包含状态和内容
    """
    try:
        from tools.roster_tool import get_life_interpretation, get_career_trend, get_daily_report, check_user_info_exists
        
        # 检查用户是否存在
        user_check = check_user_info_exists(user_id)
        if not user_check or not user_check.get("exists"):
            return json.dumps({
                "status": "failed",
                "error_code": "USER_NOT_FOUND",
                "error_message": "用户信息不存在，请先录入信息",
                "details": {"user_id": user_id}
            }, ensure_ascii=False)
        
        user_name = user_check.get("name", "用户")
        
        # 尝试从数据库读取各板块报告
        report_data = {
            "life_interpretation": None,
            "daily_fortune": None,
            "career_trend": None,
            "weather": None,
            "outfit": None
        }
        
        # 读取人生解读
        try:
            life_data = get_life_interpretation(user_id)
            if life_data:
                report_data["life_interpretation"] = life_data
        except Exception:
            pass
        
        # 读取职场大势
        try:
            career_data = get_career_trend(user_id)
            if career_data:
                report_data["career_trend"] = career_data
        except Exception:
            pass
        
        # 读取每日报告
        try:
            daily_data = get_daily_report(user_id)
            if daily_data:
                report_data["daily_fortune"] = daily_data
        except Exception:
            pass
        
        # 返回报告状态
        return json.dumps({
            "status": "success",
            "data": {
                "user_name": user_name,
                "report_data": report_data,
                "has_complete_report": all(report_data.values())
            }
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "status": "failed",
            "error_code": "REPORT_GENERATION_ERROR",
            "error_message": f"报告生成失败: {str(e)}",
            "details": {"error": str(e)}
        }, ensure_ascii=False)


@tool
def format_life_report_section(section_type: str, content: str) -> str:
    """
    格式化人生报告的各个板块为Markdown格式。
    
    Args:
        section_type: 板块类型（life/fortune/career/outfit）
        content: 板块内容
        
    Returns:
        格式化后的Markdown文本
    """
    section_titles = {
        "life": "🎯 【人生解读】",
        "fortune": "✨ 【每日运势】",
        "career": "💼 【职场大势】",
        "outfit": "👔 【今日穿搭】"
    }
    
    title = section_titles.get(section_type, "📋 【报告】")
    
    # 压缩内容长度
    if len(content) > 500:
        # 截取前500字符，添加省略号
        content = content[:500] + "\\n\\n...（更多内容请稍后刷新查看）"
    
    return f"{title}\\n\\n{content}\\n"


@tool
def check_report_cache(user_id: str, report_date: str = "") -> str:
    """
    检查用户报告缓存，返回哪些板块已有数据及是否过期。

    Args:
        user_id: 用户ID
        report_date: 查询日期（格式：YYYY-MM-DD），不填则使用今天（仅用于每日报告）

    Returns:
        JSON格式的缓存状态，包含过期信息
    """
    try:
        from tools.roster_tool import get_life_interpretation, get_career_trend, get_daily_report

        cache_status = {}

        # 检查人生解读（7天缓存）
        try:
            life_result = get_life_interpretation(user_id, check_expired=True)
            if life_result and not life_result.startswith("❌") and "已过期" not in life_result:
                cache_status["life"] = {"cached": True, "expired": False}
            elif "已过期" in life_result:
                cache_status["life"] = {"cached": True, "expired": True}
            else:
                cache_status["life"] = {"cached": False, "expired": False}
        except:
            cache_status["life"] = {"cached": False, "expired": False}

        # 检查职场大势（3个月缓存）
        try:
            career_result = get_career_trend(user_id, check_expired=True)
            if career_result and not career_result.startswith("❌") and "已过期" not in career_result:
                cache_status["career"] = {"cached": True, "expired": False}
            elif "已过期" in career_result:
                cache_status["career"] = {"cached": True, "expired": True}
            else:
                cache_status["career"] = {"cached": False, "expired": False}
        except:
            cache_status["career"] = {"cached": False, "expired": False}

        # 检查每日运势（1天缓存）
        try:
            daily_result = get_daily_report(user_id, report_date=report_date, check_expired=True)
            if daily_result and not daily_result.startswith("❌") and "已过期" not in daily_result:
                cache_status["fortune"] = {"cached": True, "expired": False}
            elif "已过期" in daily_result:
                cache_status["fortune"] = {"cached": True, "expired": True}
            else:
                cache_status["fortune"] = {"cached": False, "expired": False}
        except:
            cache_status["fortune"] = {"cached": False, "expired": False}

        # 判断是否有完整的有效缓存
        has_complete_report = all(
            section.get("cached", False) and not section.get("expired", False)
            for section in cache_status.values()
        )

        return json.dumps({
            "status": "success",
            "data": {
                "cached_sections": cache_status,
                "has_complete_report": has_complete_report,
                "cache_policy": {
                    "life": "7天",
                    "career": "3个月",
                    "fortune": "1天"
                }
            }
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "status": "failed",
            "error_code": "CACHE_CHECK_ERROR",
            "error_message": f"缓存检查失败: {str(e)}"
        }, ensure_ascii=False)
