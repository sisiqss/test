import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, ToolMessage, AIMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

# 导入工具
from tools.numerology_tool import numerology_analysis, career_advice
from tools.weather_tool import get_weather, dressing_advice
from tools.external_api_tool import bazi_api_analysis, ziwei_analysis
from tools.mbti_tool import mbti_analysis, validate_mbti_with_info
from tools.chart_tool import generate_luck_chart, predict_monthly_luck, generate_combined_chart
from tools.relationship_tool import relationship_advice, conflict_resolution
from tools.career_transition_tool import career_transition_advice, skill_gap_analysis
from tools.roster_tool import (
    add_roster_entry,
    get_roster_entries,
    get_roster_entry_by_id,
    update_roster_entry,
    delete_roster_entry,
    search_roster_entries,
    add_user_bazi,
    save_life_interpretation,
    get_life_interpretation,
    save_career_trend,
    get_career_trend,
    save_daily_report,
    get_daily_report,
    save_user_photo,
    check_user_info_exists
)
from tools.quick_report_tool import (
    generate_quick_report,
    format_life_report_section,
    check_report_cache
)
# 邀请码和消耗限制工具
from tools.invitation_code_tool import (
    generate_invitation_code,
    verify_invitation_code,
    use_invitation_code,
    list_invitation_codes,
    check_user_admin
)
from tools.usage_limit_tool import (
    check_global_usage_limit,
    check_user_usage_limit,
    record_usage,
    get_usage_statistics,
    check_all_limits
)
# from tools.daily_report_tool import (
#     get_weather_info,
#     get_fashion_trends,
#     generate_daily_fortune_report,
#     generate_dressing_suggestion,
#     upload_user_photo,
#     generate_outfit_image,
#     generate_complete_daily_report
# )
# 已注释：这些工具消耗资源较大，暂时禁用

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:] # type: ignore

class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]

@wrap_tool_call
def handle_tool_errors(request, handler):
    """
    统一处理工具执行错误，返回标准化的错误格式。
    
    错误格式：
    {
        "status": "failed",
        "error_code": "TOOL_EXECUTION_ERROR",
        "error_message": "错误描述",
        "tool_name": "工具名称"
    }
    """
    try:
        return handler(request)
    except Exception as e:
        tool_name = request.tool_call.get("name", "unknown")
        error_msg = str(e)
        
        # 返回标准化的错误响应
        error_response = {
            "status": "failed",
            "error_code": "TOOL_EXECUTION_ERROR",
            "error_message": f"工具执行失败: {error_msg}",
            "tool_name": tool_name
        }
        
        return ToolMessage(
            content=json.dumps(error_response, ensure_ascii=False),
            tool_call_id=request.tool_call["id"]
        )

def build_agent(ctx=None):
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx and not isinstance(ctx, type) else {}
    )
    
    # 注册所有工具
    tools = [
        # 命理分析工具
        bazi_api_analysis,  # 八字分析（支持外部API和降级）
        ziwei_analysis,     # 紫微斗数分析（支持外部API和降级）

        # 职场建议工具
        career_advice,      # 职场建议

        # 天气和穿搭工具
        get_weather,        # 天气查询
        dressing_advice,    # 穿搭建议

        # MBTI工具（已禁用：使用Prompt内置知识，避免联网搜索消耗资源）
        # mbti_analysis,      # MBTI分析（已禁用）
        # validate_mbti_with_info,  # MBTI与信息验证（已禁用）

        # 图表工具
        generate_luck_chart,       # 运势趋势图
        predict_monthly_luck,     # 预测月度运势
        generate_combined_chart,  # 综合趋势图

        # 人际关系工具
        relationship_advice,      # 人际关系建议
        conflict_resolution,      # 冲突解决建议

        # 职业转型工具
        career_transition_advice, # 职业转型建议
        skill_gap_analysis,       # 技能差距分析

        # 花名册工具
        add_roster_entry,         # 添加花名册条目
        get_roster_entries,       # 获取花名册列表
        get_roster_entry_by_id,   # 获取花名册条目详情
        update_roster_entry,      # 更新花名册条目
        delete_roster_entry,      # 删除花名册条目
        search_roster_entries,    # 搜索花名册条目
        add_user_bazi,           # 为用户添加八字信息
        save_life_interpretation, # 保存人生解读报告
        get_life_interpretation,  # 获取人生解读报告
        save_career_trend,       # 保存职场大势报告
        get_career_trend,        # 获取职场大势报告
        save_daily_report,       # 保存每日报告
        get_daily_report,        # 获取每日报告
        save_user_photo,         # 保存用户照片
        check_user_info_exists,  # 检查用户是否已录入信息

        # 快速报告工具
        generate_quick_report,   # 快速生成人生报告
        format_life_report_section,  # 格式化报告板块
        check_report_cache,      # 检查报告缓存

        # 邀请码管理工具
        generate_invitation_code,  # 生成邀请码（仅管理员）
        verify_invitation_code,    # 验证邀请码
        use_invitation_code,       # 使用邀请码注册
        list_invitation_codes,     # 列出邀请码（仅管理员）
        check_user_admin,          # 检查用户是否为管理员

        # 消耗限制工具
        check_global_usage_limit,  # 检查全局消耗限制
        check_user_usage_limit,   # 检查用户消耗限制
        record_usage,             # 记录消耗
        get_usage_statistics,     # 获取消耗统计（仅管理员）
        check_all_limits,         # 综合检查所有限制

        # 每日报告工具（已禁用高消耗功能）
        # get_weather_info,         # 获取天气信息（已禁用，使用get_weather替代）
        # get_fashion_trends,      # 获取流行趋势（已禁用，高消耗）
        # generate_daily_fortune_report,  # 生成每日运势报告（已禁用，使用bazi_api_analysis替代）
        # generate_dressing_suggestion,   # 生成穿搭建议（已禁用，使用dressing_advice替代）
        # upload_user_photo,       # 上传用户照片（已禁用，高消耗）
        # generate_outfit_image,   # 生成穿搭图片（已禁用，高消耗）
        # generate_complete_daily_report,  # 生成完整每日报告（已禁用，封装工具）
    ]
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
        middleware=[handle_tool_errors],
    )
