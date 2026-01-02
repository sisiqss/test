import os
import requests
from langchain.tools import tool
from typing import Any, Optional
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


# 人际关系类型数据库
RELATIONSHIP_DATABASE = {
    "同事": {
        "key_principles": ["专业边界", "相互尊重", "互利共赢", "保持适度距离"],
        "communication_style": "直接、高效、目标导向",
        "tips": [
            "工作交流时保持专业，避免过多私人话题",
            "主动提供帮助，但不要过度干涉",
            "尊重他人的工作方式和时间",
            "遇到冲突时，就事论事，不针对个人",
            "建立信任，承诺的事情要兑现"
        ],
        "mbti_tips": {
            "E": "适度参与社交，但注意不要打扰他人工作",
            "I": "主动沟通重要信息，不要过度沉默",
            "S": "注重实际细节，提供可靠的工作成果",
            "N": "分享创新想法，但要考虑可行性",
            "T": "在提出建议时，关注对方的感受",
            "F": "在沟通时注意逻辑和效率"
        }
    },
    "上司": {
        "key_principles": ["尊重权威", "主动汇报", "结果导向", "忠诚可靠"],
        "communication_style": "简明扼要、及时、正面",
        "tips": [
            "定期汇报工作进度和成果",
            "遇到问题及时反馈，带着解决方案去沟通",
            "了解上司的沟通偏好和期望",
            "主动承担有挑战性的任务",
            "维护上司的权威和形象"
        ],
        "mbti_tips": {
            "E": "主动沟通，但不要过度热情",
            "I": "确保重要信息及时汇报",
            "S": "提供具体、可靠的数据和事实",
            "N": "分享战略思考，展示远见",
            "T": "关注决策逻辑和结果",
            "F": "在提出反对意见时，先认可再表达"
        }
    },
    "下属": {
        "key_principles": ["明确目标", "及时反馈", "培养成长", "信任授权"],
        "communication_style": "清晰、鼓励、支持",
        "tips": [
            "设定清晰的期望和目标",
            "定期提供反馈，包括正面和建设性的",
            "授权给下属，给他们成长空间",
            "以身作则，建立威信",
            "关心下属的发展需求"
        ],
        "mbti_tips": {
            "E": "给他们社交机会，但注意效率",
            "I": "创造安静的思考环境",
            "S": "提供明确的指导和支持",
            "N": "鼓励创新和战略思考",
            "T": "在批评时注意方式方法",
            "F": "建立情感连接，给予关怀"
        }
    },
    "客户": {
        "key_principles": ["以客户为中心", "专业服务", "建立信任", "长期关系"],
        "communication_style": "专业、耐心、积极",
        "tips": [
            "深入了解客户需求和痛点",
            "提供专业的解决方案",
            "及时响应客户的问题和反馈",
            "管理期望，不过度承诺",
            "建立长期合作关系，而非一次性交易"
        ],
        "mbti_tips": {
            "E": "主动了解需求，但注意不要过度热情",
            "I": "耐心倾听，给予充分思考时间",
            "S": "提供具体的、可靠的服务保障",
            "N": "分享未来趋势和创新机会",
            "T": "用数据和事实建立信任",
            "F": "关注客户的感受和体验"
        }
    },
    "合作伙伴": {
        "key_principles": ["互利共赢", "信任透明", "共同目标", "资源共享"],
        "communication_style": "平等、开放、协作",
        "tips": [
            "建立共同的愿景和目标",
            "保持透明沟通，分享信息",
            "尊重彼此的利益和需求",
            "及时解决问题，不推卸责任",
            "共同成长，实现双赢"
        ],
        "mbti_tips": {
            "E": "积极沟通协调，促进合作",
            "I": "建立深度信任关系",
            "S": "提供稳定可靠的合作伙伴关系",
            "N": "共同探索创新机会",
            "T": "建立明确的合作框架",
            "F": "建立情感连接和信任"
        }
    },
    "家人": {
        "key_principles": ["关爱理解", "包容接纳", "情感支持", "共同成长"],
        "communication_style": "温暖、真诚、耐心",
        "tips": [
            "表达爱和关心",
            "尊重家庭成员的个性和选择",
            "创造高质量的相处时间",
            "学会倾听和理解",
            "包容彼此的不完美"
        ],
        "mbti_tips": {
            "E": "组织家庭活动，增进感情",
            "I": "创造安静的相处时光",
            "S": "提供实际的帮助和支持",
            "N": "分享成长和未来的规划",
            "T": "理性解决问题",
            "F": "表达情感，给予温暖"
        }
    }
}


@tool
def relationship_advice(situation: str, mbti_type: Optional[str] = None, 
                       element: Optional[str] = None, specific_issue: Optional[str] = None,
                       runtime: Any = None) -> str:
    """
    基于关系类型、MBTI和五行元素，提供人际关系建议。
    
    Args:
        situation: 关系类型（同事/上司/下属/客户/合作伙伴/家人）
        mbti_type: MBTI类型（可选，如INTJ）
        element: 五行元素（可选，如金木水火土）
        specific_issue: 具体问题或挑战（可选）
        runtime: 工具运行时对象
    
    Returns:
        人际关系建议
    """
    ctx = runtime.context
    
    # 查找关系类型信息
    relation_info = RELATIONSHIP_DATABASE.get(situation)
    
    if not relation_info:
        # 如果没有预定义的关系类型，使用联网搜索
        search_query = f"{situation} 人际关系 处理技巧 沟通建议"
        try:
            online_content = web_search(ctx, search_query, search_type="web_summary", count=3, need_summary=True)
            
            if online_content and online_content.strip():
                return f"""🤝 {situation}人际关系建议

【分析】
基于网络资料的综合分析

【专业建议】
{online_content}

💡 提示：建议结合具体情况灵活运用。
"""
        except Exception as e:
            return f"❌ 未找到关系类型「{situation}」的建议，且联网搜索失败：{str(e)}"
    
    # 构建建议
    advice_lines = [f"🤝 {situation}人际关系建议"]
    
    # 核心原则
    advice_lines.append("\n【核心原则】")
    advice_lines.extend([f"• {p}" for p in relation_info['key_principles']])
    
    # 沟通风格
    advice_lines.append("\n【沟通风格】")
    advice_lines.append(relation_info['communication_style'])
    
    # 实用建议
    advice_lines.append("\n【行动建议】")
    advice_lines.extend([f"{i+1}. {tip}" for i, tip in enumerate(relation_info['tips'])])
    
    # MBTI个性化建议
    if mbti_type:
        mbti_char = mbti_type[0].upper()
        if mbti_char in relation_info['mbti_tips']:
            advice_lines.append(f"\n【根据你的MBTI类型({mbti_type})】")
            advice_lines.append(f"• {relation_info['mbti_tips'][mbti_char]}")
    
    # 五行元素建议
    if element:
        advice_lines.append(f"\n【五行元素建议（{element}）】")
        element_tips = {
            "金": "金元素建议：保持果断和专业，但注意灵活性",
            "木": "木元素建议：发挥创造力，但注重执行力",
            "水": "水元素建议：善用智慧，但增加表达力度",
            "火": "火元素建议：保持热情，但注意控制情绪",
            "土": "土元素建议：展现稳重，但尝试创新"
        }
        advice_lines.append(element_tips.get(element, "保持平衡"))
    
    # 针对具体问题的建议
    if specific_issue:
        advice_lines.append(f"\n【关于「{specific_issue}」】")
        search_query = f"{situation} {specific_issue} 解决方案 处理技巧"
        try:
            online_content = web_search(ctx, search_query, search_type="web_summary", count=3, need_summary=True)
            if online_content and online_content.strip():
                advice_lines.append(online_content)
            else:
                advice_lines.append("• 建议寻求专业咨询或与相关方深入沟通")
        except:
            advice_lines.append("• 建议根据实际情况灵活应对")
    
    return chr(10).join(advice_lines)


@tool
def conflict_resolution(situation: str, conflict_type: str, mbti_type: Optional[str] = None,
                       runtime: Any = None) -> str:
    """
    提供冲突解决建议。
    
    Args:
        situation: 关系类型（同事/上司/下属等）
        conflict_type: 冲突类型（观点分歧/利益冲突/沟通误解/情绪对立等）
        mbti_type: MBTI类型（可选）
        runtime: 工具运行时对象
    
    Returns:
        冲突解决建议
    """
    ctx = runtime.context
    
    # 使用联网搜索获取冲突解决建议
    search_query = f"{situation} {conflict_type} 冲突解决 处理方法"
    
    try:
        online_content = web_search(ctx, search_query, search_type="web_summary", count=5, need_summary=True)
        
        advice_lines = [f"⚡ {situation} - {conflict_type}冲突解决建议"]
        
        if online_content and online_content.strip():
            advice_lines.append("\n【专业建议】")
            advice_lines.append(online_content)
        else:
            advice_lines.append("\n【通用建议】")
            advice_lines.extend([
                "1. 保持冷静，避免情绪化反应",
                "2. 主动沟通，了解对方的真实想法",
                "3. 寻找共同点和共同目标",
                "4. 控制自我，尝试换位思考",
                "5. 寻求第三方调解或专业帮助"
            ])
        
        # MBTI特定的冲突解决建议
        if mbti_type:
            mbti_char = mbti_type[0].upper()
            mbti_advice = {
                "E": "外向型：建议先私下沟通，避免公开冲突",
                "I": "内向型：建议准备充分后，主动表达想法",
                "S": "感觉型：关注具体事实和细节，避免过度理论化",
                "N": "直觉型：尝试理解整体情况，找到根本原因",
                "T": "思考型：在讲道理时，注意对方的情绪",
                "F": "情感型：表达感受时，保持客观理性"
            }
            advice_lines.append(f"\n【根据你的MBTI类型({mbti_type})】")
            advice_lines.append(f"• {mbti_advice.get(mbti_char, '保持冷静和理智')}")
        
        advice_lines.append("\n💡 温馨提示：冲突是正常的人际交往现象，关键是如何建设性地解决。")
        
        return chr(10).join(advice_lines)
        
    except Exception as e:
        return f"❌ 获取冲突建议失败：{str(e)}"
