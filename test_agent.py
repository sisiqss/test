#!/usr/bin/env python3
"""
职场情绪充电站 - 功能测试脚本
用于测试Agent的各项功能
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.agent import build_agent
from coze_coding_utils.runtime_ctx.context import new_context, Context

# 测试用例
TEST_CASES = [
    {
        "name": "命理分析",
        "prompt": "请帮我分析今天的运势"
    },
    {
        "name": "MBTI分析",
        "prompt": "我是INTJ，在职场中应该注意什么？"
    },
    {
        "name": "运势趋势图",
        "prompt": "生成我本月的运势趋势图"
    },
    {
        "name": "人际关系",
        "prompt": "如何与ENFP类型的同事更好沟通？"
    },
    {
        "name": "职业转型",
        "prompt": "我想从技术岗转产品经理，有什么建议？"
    }
]

def print_section(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

async def test_agent():
    """测试Agent功能"""
    print_section("职场情绪充电站 - 功能测试")
    
    # 构建Agent
    print("\n正在初始化Agent...")
    ctx = new_context(method="test")
    agent = build_agent(ctx)
    
    if not agent:
        print("❌ Agent初始化失败")
        return
    
    print("✅ Agent初始化成功")
    
    # 运行测试用例
    print_section("开始测试")
    
    session_id = "test_session_001"
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{len(TEST_CASES)}: {test_case['name']}")
        print(f"{'='*60}")
        print(f"用户输入: {test_case['prompt']}")
        print(f"\nAI回复:")
        print("-" * 60)
        
        try:
            # 构造输入
            payload = {
                "type": "query",
                "session_id": session_id,
                "message": test_case['prompt'],
                "content": {
                    "query": {
                        "prompt": [
                            {
                                "type": "text",
                                "content": {"text": test_case['prompt']}
                            }
                        ]
                    }
                }
            }
            
            # 运行Agent
            config = {
                "configurable": {"thread_id": session_id}
            }
            
            result = await agent.ainvoke(payload, config=config, context=ctx)
            
            # 显示结果
            if isinstance(result, dict):
                # 查找消息内容
                messages = result.get('messages', [])
                if messages:
                    # 获取最后一条AI回复
                    for msg in reversed(messages):
                        if hasattr(msg, 'content') and msg.content:
                            print(msg.content)
                            break
                else:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(str(result))
            
            print("-" * 60)
            print("✅ 测试完成")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 测试之间的延迟
        if i < len(TEST_CASES):
            print("\n⏳ 等待2秒后继续...")
            await asyncio.sleep(2)
    
    print_section("测试完成")
    print("✅ 所有测试已完成")

def main():
    """主函数"""
    print_section("欢迎来到职场情绪充电站测试程序")
    print("\n这个脚本将测试Agent的所有核心功能：")
    print("1. 🔮 命理分析")
    print("2. 🧠 MBTI分析")
    print("3. 📈 运势趋势图")
    print("4. 👥 人际关系")
    print("5. 💼 职业转型")
    
    input("\n按Enter键开始测试...")
    
    # 运行测试
    asyncio.run(test_agent())
    
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main()
