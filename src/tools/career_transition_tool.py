import os
import requests
from langchain.tools import tool
from typing import Any, Optional, List
from cozeloop.decorator import observe
from coze_coding_utils.runtime_ctx.context import Context


@observe
def web_search(
    ctx: Context,
    query: str,
    search_type: str = "web",
    count: int = 10,
    need_summary: bool = True,
):
    """联网搜索辅助函数"""
    from coze_coding_utils.runtime_ctx.context import default_headers

    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_BASE_URL")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    headers.update(default_headers(ctx))
    request = {
        "Query": query,
        "SearchType": search_type,
        "Count": count,
        "NeedSummary": need_summary,
    }
    response = requests.post(f'{base_url}/api/search_api/web_search', json=request, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    result = data.get("Result", {})
    content = None
    if result.get("Choices"):
        content = result.get("Choices", [{}])[0].get("Message", {}).get("Content", "")
    
    return content


# 行业转型数据库（示例）
INDUSTRY_TRANSITION_DATABASE = {
    "互联网": {
        "transferable_skills": [
            "项目管理",
            "数据分析",
            "产品思维",
            "用户体验设计",
            "敏捷开发",
            "跨部门协作"
        ],
        "popular_destinations": ["金融科技", "智能制造", "医疗健康", "教育科技"],
        "transition_difficulty": "中等"
    },
    "金融": {
        "transferable_skills": [
            "风险管理",
            "数据分析",
            "合规意识",
            "项目管理",
            "客户关系"
        ],
        "popular_destinations": ["金融科技", "咨询", "企业战略"],
        "transition_difficulty": "中等偏难"
    },
    "制造业": {
        "transferable_skills": [
            "流程优化",
            "质量管理",
            "供应链管理",
            "成本控制",
            "项目管理"
        ],
        "popular_destinations": ["智能制造", "工业互联网", "供应链管理"],
        "transition_difficulty": "较难"
    },
    "教育": {
        "transferable_skills": [
            "课程设计",
            "培训能力",
            "沟通表达",
            "知识传授",
            "学习辅导"
        ],
        "popular_destinations": ["教育科技", "企业培训", "内容创作", "咨询"],
        "transition_difficulty": "中等"
    },
    "医疗": {
        "transferable_skills": [
            "专业知识",
            "服务意识",
            "团队协作",
            "应急处理",
            "细致认真"
        ],
        "popular_destinations": ["医疗科技", "健康管理", "医药销售"],
        "transition_difficulty": "较难"
    }
}


@tool
def career_transition_advice(current_industry: str, target_industry: str, 
                           experience: str, current_position: str = "", 
                           mbti_type: Optional[str] = None,
                           runtime: Any = None) -> str:
    """
    提供职业转型建议。
    
    Args:
        current_industry: 当前行业
        target_industry: 目标行业
        experience: 工作年限（如：3年、5年+）
        current_position: 当前职位（可选）
        mbti_type: MBTI类型（可选）
        runtime: 工具运行时对象
    
    Returns:
        职业转型建议
    """
    ctx = runtime.context
    
    advice_lines = [f"🔄 职业转型建议：{current_industry} → {target_industry}"]
    
    # 获取可迁移技能
    current_industry_info = INDUSTRY_TRANSITION_DATABASE.get(current_industry, {})
    target_industry_info = INDUSTRY_TRANSITION_DATABASE.get(target_industry, {})
    
    if current_industry_info:
        advice_lines.append("\n【可迁移技能】")
        skills = current_industry_info.get("transferable_skills", [])
        advice_lines.extend([f"• {skill}" for skill in skills[:6]])
    
    # 联网搜索获取转型建议
    search_query = f"{current_industry}转{target_industry} 职业发展 技能要求 转型建议"
    try:
        online_content = web_search(ctx, search_query, search_type="web_summary", count=5, need_summary=True)
        
        if online_content and online_content.strip():
            advice_lines.append("\n【行业分析】")
            advice_lines.append(online_content)
    except:
        pass
    
    # 需要补充的技能
    advice_lines.append("\n【需要补充的技能】")
    advice_lines.extend([
        f"1. {target_industry}行业的专业知识",
        "2. 目标行业的证书或资质（如有）",
        "3. 行业人脉和资源",
        "4. 相关项目经验"
    ])
    
    # 学习路径
    advice_lines.append("\n【学习路径】")
    advice_lines.extend([
        "📚 在线课程：Coursera、极客时间、网易云课堂等平台的相关课程",
        "📖 专业书籍：阅读{target_industry}行业的经典书籍和最新趋势",
        "💼 实践项目：尝试在当前工作中应用{target_industry}的方法",
        "🤝 行业交流：参加行业会议、加入专业社群",
        "🎓 证书认证：如有相关证书，建议考取提升竞争力"
    ])
    
    # 时间规划
    exp_years = experience.replace("年", "").replace("+", "").strip()
    if exp_years.isdigit():
        years = int(exp_years)
        if years < 3:
            time_plan = "建议转型准备期：6-12个月"
        elif years < 5:
            time_plan = "建议转型准备期：3-6个月"
        else:
            time_plan = "建议转型准备期：3个月或更短"
    else:
        time_plan = "建议转型准备期：3-12个月（根据个人情况调整）"
    
    advice_lines.append(f"\n【时间规划】")
    advice_lines.append(f"• 总体准备期：{time_plan}")
    advice_lines.append("• 短期（1-2个月）：了解目标行业，学习基础知识")
    advice_lines.append("• 中期（3-6个月）：补充技能，尝试相关项目")
    advice_lines.append("• 长期（6-12个月）：建立人脉，开始求职或创业准备")
    
    # 风险评估
    advice_lines.append("\n【风险评估】")
    if current_industry_info:
        difficulty = current_industry_info.get("transition_difficulty", "中等")
        advice_lines.append(f"• 转型难度：{difficulty}")
    advice_lines.extend([
        "• 优势：你的{current_industry}背景在{target_industry}中可能成为差异化优势",
        "• 挑战：需要学习新知识，建立新人脉",
        "• 建议：先尝试副业或兼职体验，再决定是否全职转型"
    ])
    
    # MBTI建议
    if mbti_type:
        mbti_advice = {
            "I": "内向型建议：充分利用研究能力，深入行业知识",
            "E": "外向型建议：积极拓展人脉，参加行业活动",
            "N": "直觉型建议：关注行业趋势，把握转型时机",
            "S": "感觉型建议：注重积累实践经验，建立具体技能",
            "T": "思考型建议：理性分析，制定详细转型计划",
            "F": "情感型建议：考虑转型带来的工作满意度和幸福感"
        }
        if mbti_type[0].upper() in mbti_advice:
            advice_lines.append(f"\n【根据你的MBTI类型({mbti_type})】")
            advice_lines.append(f"• {mbti_advice[mbti_type[0].upper()]}")
    
    # 具体行动建议
    advice_lines.append("\n【具体行动建议】")
    advice_lines.extend([
        "1. 本周：阅读3篇{target_industry}行业的深度文章",
        "2. 本月：完成一个{target_industry}相关的在线课程",
        "3. 3个月内：参加{target_industry}行业活动或会议",
        "4. 6个月内：尝试在当前工作中应用{target_industry}的方法",
        "5. 1年内：开始寻找{target_industry}的工作机会或项目合作"
    ])
    
    advice_lines.append("\n💡 温馨提示：职业转型是重大决策，建议充分考虑个人兴趣、能力、市场前景和风险承受能力。必要时可寻求专业职业咨询师的帮助。")
    
    return chr(10).join(advice_lines)


@tool
def skill_gap_analysis(current_industry: str, target_industry: str, 
                     current_skills: List[str], runtime: Any = None) -> str:
    """
    分析技能差距，提供提升建议。
    
    Args:
        current_industry: 当前行业
        target_industry: 目标行业
        current_skills: 当前技能列表
        runtime: 工具运行时对象
    
    Returns:
        技能差距分析报告
    """
    ctx = runtime.context
    
    # 联网搜索目标行业所需技能
    search_query = f"{target_industry}行业 核心技能 职位要求 能力模型"
    
    try:
        online_content = web_search(ctx, search_query, search_type="web_summary", count=5, need_summary=True)
        
        analysis_lines = [f"📊 技能差距分析：{current_industry} → {target_industry}"]
        
        if online_content and online_content.strip():
            analysis_lines.append("\n【目标行业所需技能】")
            analysis_lines.append(online_content)
        else:
            analysis_lines.append("\n【目标行业所需技能】")
            analysis_lines.append("（未能获取到具体技能信息，建议根据职位JD分析）")
        
        analysis_lines.append("\n【你的现有技能】")
        analysis_lines.extend([f"• {skill}" for skill in current_skills])
        
        analysis_lines.append("\n【技能差距】")
        analysis_lines.append("• 建议对比目标行业职位要求（Job Description）进行详细分析")
        analysis_lines.append("• 识别可迁移技能和需要补充的新技能")
        
        analysis_lines.append("\n【技能提升路径】")
        analysis_lines.extend([
            "1. 确定优先级：先补充最核心的3-5项技能",
            "2. 制定学习计划：每项技能设定具体的学习目标和时间",
            "3. 实践应用：通过项目或工作练习新技能",
            "4. 获取认证：如有行业认证，建议考取",
            "5. 持续更新：技能学习是一个持续的过程"
        ])
        
        return chr(10).join(analysis_lines)
        
    except Exception as e:
        return f"❌ 技能差距分析失败：{str(e)}"
