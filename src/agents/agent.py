import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
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

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:] # type: ignore

class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]

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
        default_headers=default_headers(ctx) if ctx else {}
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
        dressing_advice,     # 穿搭建议
        
        # MBTI工具
        mbti_analysis,      # MBTI分析
        validate_mbti_with_info,  # MBTI与信息验证
        
        # 图表工具
        generate_luck_chart,       # 运势趋势图
        predict_monthly_luck,     # 预测月度运势
        generate_combined_chart,  # 综合趋势图
        
        # 人际关系工具
        relationship_advice,      # 人际关系建议
        conflict_resolution,      # 冲突解决建议
        
        # 职业转型工具
        career_transition_advice, # 职业转型建议
        skill_gap_analysis        # 技能差距分析
    ]
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
