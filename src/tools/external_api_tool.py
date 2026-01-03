import os
import json
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
    count: Optional[int] = 10,
    need_summary: Optional[bool] = True,
):
    """
    融合信息搜索API，作为降级方案使用。
    """
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
        
        return web_items, content
    except requests.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except Exception as e:
        raise Exception(f"web_search 失败: {str(e)}")


@tool
def bazi_api_analysis(birth_year: str, birth_month: str, birth_day: str, 
                      birth_hour: str, gender: str, query_date: str, runtime: Any) -> str:
    """
    使用外部八字API进行命理分析，如果API调用失败则降级到联网搜索。
    
    Args:
        birth_year: 出生年份（如：1990）
        birth_month: 出生月份（如：03）
        birth_day: 出生日（如：15）
        birth_hour: 出生时辰（0-23）
        gender: 性别（男/女）
        query_date: 查询日期（格式：YYYY-MM-DD），为空字符串则使用今天
        runtime: 工具运行时对象
    
    Returns:
        命理分析结果，包含明确的日期信息
    """
    from datetime import date
    
    ctx = runtime.context
    
    # 如果没有指定查询日期，使用今天
    if not query_date:
        query_date = date.today().strftime("%Y-%m-%d")
    
    # 检查是否配置了外部API
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    api_config_path = os.path.join(workspace_path, "config/external_apis.json")
    
    # 尝试调用外部API
    try:
        if os.path.exists(api_config_path):
            with open(api_config_path, 'r', encoding='utf-8') as f:
                api_config = json.load(f)
            
            bazi_api = api_config.get('bazi_api', {})
            
            if bazi_api.get('enabled', False):
                api_url = bazi_api.get('url')
                api_key = bazi_api.get('api_key')
                
                if api_url and api_key:
                    # 调用外部八字API（示例：腾讯云市场API）
                    # 注意：这里需要根据实际API文档调整请求格式
                    response = requests.post(
                        api_url,
                        json={
                            "birth_year": birth_year,
                            "birth_month": birth_month,
                            "birth_day": birth_day,
                            "birth_hour": birth_hour,
                            "gender": gender,
                            "query_date": query_date,  # 添加查询日期参数
                            "api_key": api_key
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # 解析API返回的数据
                        return parse_bazi_api_response(data, birth_year, birth_month, birth_day, birth_hour, gender, query_date)
    except Exception as e:
        print(f"外部API调用失败，降级到联网搜索: {str(e)}")
    
    # 降级到联网搜索
    return fallback_bazi_analysis(ctx, birth_year, birth_month, birth_day, birth_hour, gender, query_date)


def parse_bazi_api_response(data: dict, birth_year: str, birth_month: str, 
                             birth_day: str, birth_hour: str, gender: str, query_date: str) -> str:
    """解析八字API的返回数据"""
    # 这里需要根据实际API的返回格式进行解析
    # 以下是示例解析逻辑
    
    try:
        # 假设API返回格式（需要根据实际API文档调整）
        eight_chars = data.get("eight_characters", "")
        five_elements = data.get("five_elements", {})
        today_luck = data.get("today_luck", "")
        lucky_color = data.get("lucky_color", "")
        
        return f"""🎯 命理分析报告（专业API）

【查询日期】{query_date}
【出生信息】
{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时 | 性别：{gender}

【八字排盘】
{eight_chars}

【五行分析】
{json.dumps(five_elements, ensure_ascii=False, indent=2)}

【今日运势】
{today_luck}

【幸运颜色】
{lucky_color}

⚠️ 提醒：以上分析仅供娱乐参考，实际决策请结合现实情况。
"""
    except Exception as e:
        raise Exception(f"API数据解析失败: {str(e)}")


def fallback_bazi_analysis(ctx: Context, birth_year: str, birth_month: str, 
                           birth_day: str, birth_hour: str, gender: str, query_date: str) -> str:
    """降级方案：使用联网搜索获取命理信息"""
    query = f"{query_date} {birth_year}年{birth_month}月{birth_day}日{birth_hour}时出生{gender}性 八字排盘 五行分析 运势"
    
    try:
        web_items, content = web_search(ctx, query, search_type="web_summary", count=5, need_summary=True)
        
        if content and content.strip():
            return f"""🎯 命理分析报告（联网搜索）

【查询日期】{query_date}
【出生信息】
{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时 | 性别：{gender}

【命理分析】
{content}

⚠️ 提醒：以上分析仅供参考，实际决策请结合现实情况。
"""
        else:
            results = []
            for item in web_items[:3]:
                results.append(f"- {item.get('Title', '')}: {item.get('Snippet', '')}")
            
            return f"""🎯 命理分析报告（联网搜索）

【查询日期】{query_date}
【出生信息】
{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时 | 性别：{gender}

【命理分析】
{chr(10).join(results) if results else '暂未获取到详细信息，请稍后再试。'}

⚠️ 提醒：以上分析仅供参考，实际决策请结合现实情况。
"""
    except Exception as e:
        return f"命理分析失败：{str(e)}"


@tool
def ziwei_analysis(birth_year: str, birth_month: str, birth_day: str, 
                  birth_hour: str, gender: str, query_date: str, runtime: Any) -> str:
    """
    使用外部紫微斗数API进行分析，如果API调用失败则降级到联网搜索。
    
    Args:
        birth_year: 出生年份（如：1990）
        birth_month: 出生月份（如：03）
        birth_day: 出生日（如：15）
        birth_hour: 出生时辰（0-23）
        gender: 性别（0=女, 1=男）
        query_date: 查询日期（格式：YYYY-MM-DD），为空字符串则使用今天
        runtime: 工具运行时对象
    
    Returns:
        紫微斗数分析结果，包含明确的日期信息
    """
    from datetime import date
    
    ctx = runtime.context
    
    # 如果没有指定查询日期，使用今天
    if not query_date:
        query_date = date.today().strftime("%Y-%m-%d")
    
    # 转换性别
    gender_code = "1" if gender == "男" else "0"
    
    # 检查是否配置了外部API
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    api_config_path = os.path.join(workspace_path, "config/external_apis.json")
    
    # 尝试调用外部API
    try:
        if os.path.exists(api_config_path):
            with open(api_config_path, 'r', encoding='utf-8') as f:
                api_config = json.load(f)
            
            ziwei_api = api_config.get('ziwei_api', {})
            
            if ziwei_api.get('enabled', False):
                api_url = ziwei_api.get('url')
                api_key = ziwei_api.get('api_key')
                
                if api_url and api_key:
                    # 调用外部紫微斗数API（示例：江阴雨辰互联API）
                    response = requests.post(
                        api_url,
                        data={
                            "name": "用户",
                            "sex": gender_code,
                            "type": "0",  # 0表示公历
                            "year": birth_year,
                            "month": birth_month,
                            "day": birth_day,
                            "hours": birth_hour,
                            "minute": "00",
                            "api_key": api_key
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return parse_ziwei_api_response(data, birth_year, birth_month, birth_day, birth_hour, gender, query_date)
    except Exception as e:
        print(f"紫微斗数API调用失败，降级到联网搜索: {str(e)}")
    
    # 降级到联网搜索
    return fallback_ziwei_analysis(ctx, birth_year, birth_month, birth_day, birth_hour, gender, query_date)


def parse_ziwei_api_response(data: dict, birth_year: str, birth_month: str, 
                            birth_day: str, birth_hour: str, gender: str, query_date: str) -> str:
    """解析紫微斗数API的返回数据"""
    try:
        # 假设API返回格式（需要根据实际API文档调整）
        mingpan = data.get("mingpan", {})
        star_info = mingpan.get("star_info", "")
        palace_info = mingpan.get("palace_info", "")
        
        return f"""🔮 紫微斗数命盘分析（专业API）

【查询日期】{query_date}
【出生信息】
{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时 | 性别：{gender}

【紫微命盘】
{star_info}

【十二宫位】
{palace_info}

⚠️ 提醒：以上分析仅供娱乐参考，实际决策请结合现实情况。
"""
    except Exception as e:
        raise Exception(f"紫微斗数API数据解析失败: {str(e)}")


def fallback_ziwei_analysis(ctx: Context, birth_year: str, birth_month: str, 
                            birth_day: str, birth_hour: str, gender: str, query_date: str) -> str:
    """降级方案：使用联网搜索获取紫微斗数信息"""
    query = f"{query_date} {birth_year}年{birth_month}月{birth_day}日{birth_hour}时出生{gender}性 紫微斗数 排盘 命盘 运势"
    
    try:
        web_items, content = web_search(ctx, query, search_type="web_summary", count=5, need_summary=True)
        
        if content and content.strip():
            return f"""🔮 紫微斗数命盘分析（联网搜索）

【查询日期】{query_date}
【出生信息】
{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时 | 性别：{gender}

【紫微斗数分析】
{content}

⚠️ 提醒：以上分析仅供参考，实际决策请结合现实情况。
"""
        else:
            results = []
            for item in web_items[:3]:
                results.append(f"- {item.get('Title', '')}: {item.get('Snippet', '')}")
            
            return f"""🔮 紫微斗数命盘分析（联网搜索）

【查询日期】{query_date}
【出生信息】
{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时 | 性别：{gender}

【紫微斗数分析】
{chr(10).join(results) if results else '暂未获取到详细信息，请稍后再试。'}

⚠️ 提醒：以上分析仅供参考，实际决策请结合现实情况。
"""
    except Exception as e:
        return f"紫微斗数分析失败：{str(e)}"
