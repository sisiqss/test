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
def get_weather(city: str, runtime: Any) -> str:
    """
    查询指定城市的天气信息。
    
    Args:
        city: 城市名称（如：北京、上海）
        runtime: 工具运行时对象
    
    Returns:
        天气信息字符串，包含温度、天气状况等
    """
    ctx = runtime.context
    
    # 构建搜索查询
    query = f"{city}今天天气 温度 穿搭"
    
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
            return f"""🌤️ {city}天气信息

【天气概况】
{content}

"""
        else:
            # 如果没有总结内容，使用搜索结果列表
            results = []
            for item in web_items[:3]:
                results.append(f"- {item.get('Title', '')}: {item.get('Snippet', '')}")
            
            return f"""🌤️ {city}天气信息

【天气概况】
{chr(10).join(results) if results else '暂未获取到天气信息，请稍后再试。'}

"""
    except Exception as e:
        return f"天气查询失败：{str(e)}"


@tool
def dressing_advice(industry: str, weather: str, lucky_color: str, runtime: Any) -> str:
    """
    根据行业、天气和幸运色提供穿搭建议。
    
    Args:
        industry: 行业（如：互联网、金融、教育）
        weather: 天气描述（如：晴天、下雨、寒冷）
        lucky_color: 幸运色（如：红色、蓝色、白色）
        runtime: 工具运行时对象
    
    Returns:
        穿搭建议字符串
    """
    ctx = runtime.context
    
    # 构建搜索查询
    query = f"{industry}行业 {weather}天气 职场穿搭"
    
    try:
        web_items, content, result = web_search(
            ctx=ctx,
            query=query,
            search_type="web_summary",
            count=5,
            need_summary=True
        )
        
        # 构建返回结果
        base_advice = ""
        if content and content.strip():
            base_advice = content
        else:
            # 如果没有总结内容，使用搜索结果列表
            results = []
            for item in web_items[:2]:
                results.append(f"- {item.get('Snippet', '')}")
            base_advice = chr(10).join(results) if results else "建议穿着舒适得体的服装"
        
        return f"""👔 穿搭建议

【基础风格】{base_advice}

【今日搭配】
- 主色调：适合{lucky_color}色系
- 风格建议：根据{weather}天气调整
- 配饰提示：可添加{lucky_color}色配饰提升运势

💡 提示：保持专业形象的同时，也要注意舒适度哦！
"""
    except Exception as e:
        return f"穿搭建议获取失败：{str(e)}"
