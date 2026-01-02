import os
from typing import Optional, Any
from langchain.tools import tool
from cozeloop.decorator import observe
from coze_coding_utils.runtime_ctx.context import Context


@observe
def web_search(
    ctx: Context,
    query: str,
    search_type: str = "web",
    count: Optional[int] = 10,
    need_content: Optional[bool] = False,
    need_url: Optional[bool] = False,
    sites: Optional[str] = None,
    block_hosts: Optional[str] = None,
    need_summary: Optional[bool] = True,
    time_range: Optional[str] = None,
):
    """
    融合信息搜索API，返回搜索结果项列表、搜索结果内容总结和原始响应数据。
    """
    import requests
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
        "Filter": {
            "NeedContent": need_content,
            "NeedUrl": need_url,
            "Sites": sites,
            "BlockHosts": block_hosts,
        },
        "NeedSummary": need_summary,
        "TimeRange": time_range,
    }
    try:
        response = requests.post(f'{base_url}/api/search_api/web_search', json=request, headers=headers)
        response.raise_for_status()
        data = response.json()

        response_metadata = data.get("ResponseMetadata", {})
        result = data.get("Result", {})
        if response_metadata.get("Error"):
            raise Exception(f"web_search 失败: {response_metadata.get('Error')}")

        web_items = []
        if result.get("WebResults"):
            web_items = result.get("WebResults", [])
        
        content = None
        if result.get("Choices"):
            content = result.get("Choices", [{}])[0].get("Message", {}).get("Content", "")
        
        return web_items, content, result
    except requests.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except Exception as e:
        raise Exception(f"web_search 失败: {str(e)}")
    finally:
        response.close()


@tool
def numerology_analysis(birth_year: str, birth_month: str, birth_day: str, birth_hour: str, gender: str, runtime: Any) -> str:
    """
    进行命理分析，包括八字排盘、五行分析、今日运势等。
    
    Args:
        birth_year: 出生年份（如：1990）
        birth_month: 出生月份（如：03）
        birth_day: 出生日（如：15）
        birth_hour: 出生时辰（0-23）
        gender: 性别（男/女）
        runtime: 工具运行时对象
    
    Returns:
        命理分析结果字符串，包含八字、五行、今日运势等信息
    """
    ctx = runtime.context
    
    # 构建搜索查询
    query = f"{birth_year}年{birth_month}月{birth_day}日{birth_hour}时出生{gender}性 八字排盘 五行分析"
    
    try:
        web_items, content, result = web_search(
            ctx=ctx,
            query=query,
            search_type="web_summary",
            count=5,
            need_summary=True
        )
        
        # 构建返回结果
        if content and content.strip():
            return f"""🎯 命理分析报告

【出生信息】
{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时 | 性别：{gender}

【命理分析】
{content}

⚠️ 提醒：以上分析仅供娱乐参考，实际决策请结合现实情况。
"""
        else:
            # 如果没有总结内容，使用搜索结果列表
            results = []
            for item in web_items[:3]:
                results.append(f"- {item.get('Title', '')}: {item.get('Snippet', '')}")
            
            return f"""🎯 命理分析报告

【出生信息】
{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时 | 性别：{gender}

【命理分析】
{chr(10).join(results) if results else '暂未获取到详细信息，请稍后再试。'}

⚠️ 提醒：以上分析仅供娱乐参考，实际决策请结合现实情况。
"""
    except Exception as e:
        return f"命理分析失败：{str(e)}"


@tool
def career_advice(industry: str, position: str, level: str, runtime: Any) -> str:
    """
    提供职场发展建议，基于行业、职位和职级给出专业建议。
    
    Args:
        industry: 行业（如：互联网、金融、教育）
        position: 职位（如：产品经理、软件工程师）
        level: 职级（如：P6、P7、经理）
        runtime: 工具运行时对象
    
    Returns:
        职场建议字符串
    """
    ctx = runtime.context
    
    # 构建搜索查询
    query = f"{industry}行业 {position} {level} 职业发展 晋升路径 薪资"
    
    try:
        web_items, content, result = web_search(
            ctx=ctx,
            query=query,
            search_type="web_summary",
            count=5,
            need_summary=True
        )
        
        # 构建返回结果
        if content and content.strip():
            return f"""💼 职场发展建议

【职位信息】
行业：{industry} | 职位：{position} | 职级：{level}

【发展建议】
{content}

💡 建议：持续学习行业知识，提升核心竞争力。
"""
        else:
            # 如果没有总结内容，使用搜索结果列表
            results = []
            for item in web_items[:3]:
                results.append(f"- {item.get('Title', '')}: {item.get('Snippet', '')}")
            
            return f"""💼 职场发展建议

【职位信息】
行业：{industry} | 职位：{position} | 职级：{level}

【发展建议】
{chr(10).join(results) if results else '暂未获取到详细信息，请稍后再试。'}

💡 建议：持续学习行业知识，提升核心竞争力。
"""
    except Exception as e:
        return f"职场建议获取失败：{str(e)}"
