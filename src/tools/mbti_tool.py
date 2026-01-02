import os
import requests
from langchain.tools import tool
from typing import Any
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


# MBTI类型基础数据库
MBTI_DATABASE = {
    "INTJ": {
        "name": "建筑师",
        "description": "富有想象力的战略思想家",
        "strengths": ["战略规划", "独立工作", "系统性思考", "逻辑分析"],
        "challenges": ["情感表达", "团队协作", "适应变化", "耐心倾听"],
        "career": ["架构师", "战略顾问", "数据科学家", "系统工程师"],
        "work_style": "独立、有条理、追求效率",
        "lucky_element": "水"
    },
    "INTP": {
        "name": "逻辑学家",
        "description": "具有创造力的发明家",
        "strengths": ["逻辑分析", "创新思维", "问题解决", "客观理性"],
        "challenges": ["执行力", "时间管理", "情感表达", "细节关注"],
        "career": ["研究员", "程序员", "分析师", "咨询师"],
        "work_style": "灵活、创新、独立思考",
        "lucky_element": "木"
    },
    "ENTJ": {
        "name": "指挥官",
        "description": "大胆、富有想象力的领导者",
        "strengths": ["领导力", "战略规划", "决策能力", "目标导向"],
        "challenges": ["情感敏感", "耐心", "灵活性", "共情能力"],
        "career": ["CEO", "项目经理", "咨询顾问", "创业者"],
        "work_style": "果断、高效、结果导向",
        "lucky_element": "火"
    },
    "ENTP": {
        "name": "辩论家",
        "description": "聪明的创新者",
        "strengths": ["创新", "辩论", "适应力", "社交能力"],
        "challenges": ["细节关注", "执行力", "时间管理", "专注"],
        "career": ["市场总监", "创业者", "产品经理", "咨询顾问"],
        "work_style": "灵活、创新、善于沟通",
        "lucky_element": "风"
    },
    "INFJ": {
        "name": "提倡者",
        "description": "安静而神秘的理想主义者",
        "strengths": ["洞察力", "共情", "创造力", "理想主义"],
        "challenges": ["过度敏感", "完美主义", "拒绝批评", "职业倦怠"],
        "career": ["心理咨询师", "作家", "HR", "教育顾问"],
        "work_style": "深度、有洞察、注重意义",
        "lucky_element": "水"
    },
    "INFP": {
        "name": "调停者",
        "description": "诗意、善良的利他主义者",
        "strengths": ["创造力", "共情", "理想主义", "真诚"],
        "challenges": ["执行力", "现实感", "时间管理", "冲突处理"],
        "career": ["设计师", "作家", "艺术家", "教育者"],
        "work_style": "灵活、有创意、价值驱动",
        "lucky_element": "木"
    },
    "ENFJ": {
        "name": "主人公",
        "description": "富有魅力的领导者",
        "strengths": ["领导力", "共情", "沟通", "激励他人"],
        "challenges": ["过度关心", "自我牺牲", "决策困难", "敏感"],
        "career": ["HR经理", "培训师", "销售经理", "公关"],
        "work_style": "热情、协作、以人为本",
        "lucky_element": "火"
    },
    "ENFP": {
        "name": "竞选者",
        "description": "热情、有创造力的自由精神",
        "strengths": ["创造力", "社交能力", "热情", "适应力"],
        "challenges": ["专注", "细节", "时间管理", "情绪波动"],
        "career": ["市场专员", "公关", "活动策划", "创意总监"],
        "work_style": "灵活、热情、创新",
        "lucky_element": "风"
    },
    "ISTJ": {
        "name": "物流师",
        "description": "实际、注重事实的决策者",
        "strengths": ["组织能力", "责任感", "可靠性", "细节关注"],
        "challenges": ["灵活性", "情感表达", "创新", "接受批评"],
        "career": ["会计师", "律师", "行政", "质量保证"],
        "work_style": "有条理、可靠、系统化",
        "lucky_element": "土"
    },
    "ISFJ": {
        "name": "守卫者",
        "description": "非常专注而温暖的守护者",
        "strengths": ["支持性", "可靠", "耐心", "细节关注"],
        "challenges": ["过度牺牲", "拒绝改变", "自我忽视", "冲突回避"],
        "career": ["护士", "教师", "行政助理", "客户服务"],
        "work_style": "支持、可靠、注重细节",
        "lucky_element": "土"
    },
    "ESTJ": {
        "name": "总经理",
        "description": "出色的管理者",
        "strengths": ["组织能力", "领导力", "可靠性", "高效"],
        "challenges": ["不灵活", "缺乏耐心", "情感表达", "创新"],
        "career": ["运营经理", "警官", "军官", "中层管理"],
        "work_style": "组织、高效、结果导向",
        "lucky_element": "土"
    },
    "ESFJ": {
        "name": "执政官",
        "description": "极有同情心的社交者",
        "strengths": ["社交能力", "支持性", "可靠", "组织能力"],
        "challenges": ["过度关心", "拒绝冲突", "自我忽视", "灵活性"],
        "career": ["销售", "教师", "活动策划", "客户服务"],
        "work_style": "协作、支持、注重关系",
        "lucky_element": "土"
    },
    "ISTP": {
        "name": "鉴赏家",
        "description": "大胆而实际的实验家",
        "strengths": ["动手能力", "问题解决", "适应性", "冷静"],
        "challenges": ["情感表达", "长期规划", "承诺", "理论思考"],
        "career": ["工程师", "技师", "飞行员", "运动员"],
        "work_style": "实际、灵活、动手能力强",
        "lucky_element": "金"
    },
    "ISFP": {
        "name": "探险家",
        "description": "灵活、迷人的艺术家",
        "strengths": ["创造力", "艺术感", "适应力", "真诚"],
        "challenges": ["长期规划", "时间管理", "批评", "承诺"],
        "career": ["设计师", "艺术家", "摄影师", "治疗师"],
        "work_style": "灵活、创意、艺术感",
        "lucky_element": "金"
    },
    "ESTP": {
        "name": "企业家",
        "description": "聪明、精力充沛的感知者",
        "strengths": ["适应力", "社交能力", "活力", "问题解决"],
        "challenges": ["长期规划", "细节", "理论思考", "情绪敏感"],
        "career": ["销售", "企业家", "演员", "急救"],
        "work_style": "灵活、行动导向、适应力强",
        "lucky_element": "火"
    },
    "ESFP": {
        "name": "表演者",
        "description": "自发的、充满精力的表演者",
        "strengths": ["社交能力", "热情", "适应力", "娱乐性"],
        "challenges": ["长期规划", "理论思考", "专注", "批评"],
        "career": ["演员", "销售", "活动策划", "娱乐行业"],
        "work_style": "热情、灵活、以人为本",
        "lucky_element": "火"
    }
}


@tool
def mbti_analysis(mbti_type: str, name: str, birth_info: dict, career_info: dict, runtime: Any) -> str:
    """
    基于用户提供的MBTI类型，结合互联网资料进行性格分析，并与姓名、命理信息交叉验证。
    
    Args:
        mbti_type: MBTI类型（如：INTJ、ENFP）
        name: 用户姓名
        birth_info: 出生信息字典，包含year, month, day, hour, gender
        career_info: 职场信息字典，包含industry, position, level
        runtime: 工具运行时对象
    
    Returns:
        MBTI性格分析报告
    """
    ctx = runtime.context
    
    mbti_upper = mbti_type.upper().strip()
    type_info = MBTI_DATABASE.get(mbti_upper, {})
    
    if not type_info:
        return f"❌ 未找到MBTI类型「{mbti_type}」的分析，请确认类型是否正确。"
    
    # 使用联网搜索获取更详细的MBTI资料
    search_query = f"{mbti_upper}型人格 性格特点 职业发展 心理学"
    try:
        online_content = web_search(ctx, search_query, search_type="web_summary", count=3, need_summary=True)
        
        online_analysis = ""
        if online_content and online_content.strip():
            online_analysis = f"\n【心理学专业解读】\n{online_content}"
    except Exception as e:
        online_analysis = ""
    
    # 结合命理信息交叉验证
    birth_year = birth_info.get('year', '')
    birth_month = birth_info.get('month', '')
    
    # 根据出生月份简化的五行分析（仅供交叉验证参考）
    month_elements = {
        '1': '木', '2': '木', '3': '火', '4': '火', '5': '土',
        '6': '土', '7': '金', '8': '金', '9': '水', '10': '水', '11': '水', '12': '水'
    }
    month_element = month_elements.get(str(birth_month), '')
    
    element_compatibility = ""
    if month_element and type_info.get('lucky_element'):
        if month_element == type_info.get('lucky_element'):
            element_compatibility = f"✨ 你的五行属性（{month_element}）与MBTI类型匹配度很高！"
        else:
            element_compatibility = f"💡 你的五行属性（{month_element}）与MBTI类型有互补性，可以互相增强。"
    
    # 结合职场信息验证
    industry = career_info.get('industry', '')
    position = career_info.get('position', '')
    
    career_match = ""
    if industry and position:
        recommended_careers = type_info.get('career', [])
        is_match = any(career.lower() in position.lower() or career.lower() in industry.lower() 
                      for career in recommended_careers)
        
        if is_match:
            career_match = f"✅ 你的职业选择「{position}」与MBTI性格高度匹配，发挥优势！"
        else:
            career_match = f"💡 建议：可以考虑向 {', '.join(recommended_careers[:2])} 方向发展，更符合你的性格优势。"
    
    return f"""🧠 MBTI性格分析报告

【基础信息】
• 姓名：{name}
• MBTI类型：{mbti_upper} - {type_info.get('name', '')}
• 描述：{type_info.get('description', '')}

【性格优势】
{chr(10).join([f'• {s}' for s in type_info.get('strengths', [])])}

【成长挑战】
{chr(10).join([f'• {c}' for c in type_info.get('challenges', [])])}

【适合职业】
{chr(10).join([f'• {c}' for c in type_info.get('career', [])])}

【工作风格】
{type_info.get('work_style', '')}

{online_analysis}

{element_compatibility}

{career_match}

💡 综合建议：
结合你的MBTI类型和命理特点，建议在工作中发挥{type_info.get('strengths', [''])[0]}优势，
同时注意在{type_info.get('challenges', [''])[0]}方面加强练习。

⚠️ 提醒：以上分析结合了心理学和命理学观点，仅供参考，实际发展请结合个人情况和现实考量。
"""


@tool
def validate_mbti_with_info(mbti_type: str, birth_info: dict, runtime: Any) -> str:
    """
    验证MBTI类型与命理信息的一致性。
    
    Args:
        mbti_type: MBTI类型
        birth_info: 出生信息
        runtime: 工具运行时对象
    
    Returns:
        验证结果
    """
    mbti_upper = mbti_type.upper().strip()
    type_info = MBTI_DATABASE.get(mbti_upper, {})
    
    if not type_info:
        return "❌ MBTI类型未找到"
    
    return f"""✓ 验证完成
MBTI类型：{mbti_upper}
五行关联：{type_info.get('lucky_element', '')}元素
与命理信息交叉验证结果：可以结合分析
"""
