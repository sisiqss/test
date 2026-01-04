"""
后端 API 服务 - Render 部署版本
提供统一的接口供前端调用 Agent 工具
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.agents.agent import build_agent
from langgraph.checkpoint.memory import MemorySaver
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许跨域

# 禁用自动重定向
app.url_map.strict_slashes = False

# Render 环境变量配置
# Render 会自动提供 PORT 环境变量
API_PORT = int(os.getenv('PORT', '10000'))  # Render 默认端口
API_HOST = os.getenv('HOST', '0.0.0.0')
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'

# 构建 Agent（全局单例）
logger.info("🔧 正在构建 Agent...")
try:
    agent = build_agent()
    checkpointer = MemorySaver()
    logger.info("✅ Agent 构建成功")
except Exception as e:
    logger.error(f"❌ Agent 构建失败: {e}")
    logger.error(f"请检查 COZE_WORKSPACE_PATH 和依赖是否正确")
    raise


@app.route('/')
def index():
    """首页"""
    return jsonify({
        'status': 'ok',
        'message': '职场情绪充电站 API 服务',
        'service': 'Agent API',
        'endpoints': {
            'health': '/api/health',
            'tools': '/api/tools',
            'chat': '/api/agent/chat'
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'message': 'Agent API 服务正常运行',
        'timestamp': str(app.config.get('START_TIME', 'unknown'))
    })


@app.route('/api/agent/chat', methods=['POST', 'OPTIONS'])
def agent_chat():
    """统一调用 Agent 工具的接口"""
    # 处理 OPTIONS 请求（CORS 预检）
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.json

        # 获取参数
        user_id = data.get('user_id')
        tool_name = data.get('tool_name')
        tool_params = data.get('tool_params', {})
        message = data.get('message', '')

        # 验证必需参数
        if not user_id:
            return jsonify({
                'status': 'failed',
                'error_code': 'MISSING_REQUIRED_PARAM',
                'error_message': '缺少必需参数: user_id'
            }), 400

        # 如果指定了工具名称，直接调用工具
        if tool_name:
            logger.info(f"🔧 直接调用工具: {tool_name} | user_id: {user_id}")

            # 找到对应的工具（从 agent.nodes['tools'].bound.tools_by_name 获取）
            tool = None
            tools_node = agent.nodes.get('tools')
            if tools_node and hasattr(tools_node, 'bound'):
                bound = tools_node.bound
                if hasattr(bound, 'tools_by_name'):
                    tool = bound.tools_by_name.get(tool_name)

            if not tool:
                return jsonify({
                    'status': 'failed',
                    'error_code': 'TOOL_NOT_FOUND',
                    'error_message': f'工具不存在: {tool_name}'
                }), 404

            # 调用工具
            try:
                # 如果工具参数中没有 user_id，自动添加
                if 'user_id' not in tool_params:
                    tool_params['user_id'] = user_id

                # 调用工具
                result = tool.invoke(tool_params)

                logger.info(f"✅ 工具调用成功: {tool_name}")

                return jsonify({
                    'status': 'success',
                    'data': result,
                    'tool_name': tool_name
                })

            except Exception as e:
                logger.error(f"❌ 工具调用失败: {tool_name} | 错误: {e}")
                return jsonify({
                    'status': 'failed',
                    'error_code': 'TOOL_EXECUTION_ERROR',
                    'error_message': str(e),
                    'tool_name': tool_name
                }), 500

        # 否则发送消息给 Agent
        logger.info(f"💬 发送消息给 Agent | user_id: {user_id}")

        config = {"configurable": {"thread_id": user_id}}

        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": message}]},
                config
            )

            logger.info(f"✅ Agent 响应成功 | user_id: {user_id}")

            return jsonify({
                'status': 'success',
                'data': response
            })

        except Exception as e:
            logger.error(f"❌ Agent 调用失败 | user_id: {user_id} | 错误: {e}")
            return jsonify({
                'status': 'failed',
                'error_code': 'AGENT_EXECUTION_ERROR',
                'error_message': str(e)
            }), 500

    except Exception as e:
        logger.error(f"❌ API 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'failed',
            'error_code': 'INTERNAL_ERROR',
            'error_message': str(e)
        }), 500


@app.route('/api/tools', methods=['GET'])
def list_tools():
    """获取所有可用工具列表"""
    try:
        tools = []
        # 从 agent.nodes['tools'].bound.tools_by_name 获取
        tools_node = agent.nodes.get('tools')
        if tools_node and hasattr(tools_node, 'bound'):
            bound = tools_node.bound
            if hasattr(bound, 'tools_by_name'):
                for name, tool in bound.tools_by_name.items():
                    tools.append({
                        'name': name,
                        'description': tool.description,
                        'parameters': tool.args_schema.schema() if tool.args_schema else {}
                    })

        return jsonify({
            'status': 'success',
            'total': len(tools),
            'tools': tools
        })

    except Exception as e:
        logger.error(f"❌ 获取工具列表失败: {e}")
        return jsonify({
            'status': 'failed',
            'error_message': str(e)
        }), 500


if __name__ == '__main__':
    app.config['START_TIME'] = os.getenv('START_TIME', '')

    print("=" * 60)
    print("🚀 Agent API 服务启动 (Render)")
    print("=" * 60)
    print(f"🌐 监听主机: {API_HOST}:{API_PORT}")
    print(f"📊 健康检查: /api/health")
    print(f"🔧 Agent 聊天: /api/agent/chat")
    print(f"🛠️ 工具列表: /api/tools")
    print(f"🐛 调试模式: {DEBUG_MODE}")
    print("=" * 60)

    # 启动服务
    app.run(
        host=API_HOST,
        port=API_PORT,
        debug=DEBUG_MODE
    )
