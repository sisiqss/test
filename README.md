# 职场情绪充电站 AI Agent

一个基于 LangChain 的职场情绪充电站 AI Agent，集成命理分析、职场咨询、情绪支持和实用建议功能。

## ✨ 功能特性

- 🔮 **命理分析**：八字、紫微斗数运势分析
- 🧠 **MBTI分析**：性格分析与职场建议
- 📈 **运势趋势图**：可视化运势变化趋势
- 👥 **人际关系**：性格匹配与沟通建议
- 💼 **职业转型**：可迁移技能分析与转型路径

## 🚀 快速开始

### ⭐ 方式一：启动 HTTP 服务（推荐）

这是最简单直接的使用方式，直接在本地启动 HTTP 服务，通过浏览器访问。

```bash
# 启动 HTTP 服务（默认端口 8000）
bash scripts/http_run.sh -p 8000
```

然后在浏览器中打开：`http://localhost:8000`

#### 如何使用：
1. 启动服务后，在浏览器中访问 `http://localhost:8000`
2. 在聊天框中发送消息，例如："你好"
3. 按照提示提供个人信息（昵称、出生时间等）
4. 获取完整的职场情绪充电报告
5. 继续对话，享受各项功能

#### 功能示例：
- 🔮 "请帮我分析今天的运势"
- 🧠 "我是INTJ，在职场中应该注意什么？"
- 📈 "生成我本月的运势趋势图"
- 👥 "如何与ENFP类型的同事更好沟通？"
- 💼 "我想从技术岗转产品经理，有什么建议？"

---

### 方式二：命令行测试

适用于开发测试，直接在命令行中运行 Agent。

```bash
# 测试Agent
bash scripts/local_run.sh -m agent
```

---

## 📚 详细文档

### 功能文档
- [功能总结](docs/FEATURE_SUMMARY.md) - 完整功能说明

## 🎯 项目结构

```
.
├── config                   # 配置文件
│   ├── agent_llm_config.json  # 模型配置
│   └── external_apis.json      # 外部API配置
├── docs                      # 文档
│   └── FEATURE_SUMMARY.md    # 功能总结
├── src                       # 源代码
│   ├── agents                 # Agent代码
│   │   └── agent.py           # 主Agent
│   ├── tools                  # 工具代码
│   │   ├── external_api_tool.py  # 外部API工具
│   │   ├── mbti_tool.py           # MBTI分析工具
│   │   ├── chart_tool.py          # 图表生成工具
│   │   ├── relationship_tool.py   # 人际关系工具
│   │   └── career_transition_tool.py  # 职业转型工具
│   ├── storage                # 存储
│   └── main.py                # 主入口
├── scripts                   # 脚本
│   ├── http_run.sh           # 启动HTTP服务
│   ├── local_run.sh          # 本地运行
│   └── load_env.sh           # 加载环境变量
├── test_agent.py            # 测试脚本
├── requirements.txt          # 依赖包
└── README.md                # 本文件
```

## ⚙️ 配置说明

所有配置文件位于 `config/` 目录：
- `agent_llm_config.json` - 模型配置
- `external_apis.json` - 外部API配置

## 🛠️ 技术栈

- **框架**：LangChain, LangGraph
- **模型**：deepseek-r1-250528
- **数据可视化**：QuickChart API
- **搜索**：联网搜索集成

## 🤔 常见问题

### Q1: 如何启动 Agent？

**A**: 最简单的方式是启动 HTTP 服务：
```bash
bash scripts/http_run.sh -p 8000
```
然后在浏览器中访问 `http://localhost:8000`

### Q2: 可以修改端口号吗？

**A**: 可以，使用 `-p` 参数指定端口：
```bash
bash scripts/http_run.sh -p 9000
```

### Q3: 为什么 Agent 没有立即回复？

**A**: Agent 需要调用多个工具（联网搜索、天气查询、八字分析等），这些操作可能需要几秒钟，请耐心等待。

### Q4: 支持哪些功能？

**A**:
- 🔮 命理分析：八字、紫微斗数运势分析
- 🧠 MBTI分析：性格分析与职场建议
- 📈 运势趋势图：可视化运势变化趋势
- 👥 人际关系：性格匹配与沟通建议
- 💼 职业转型：可迁移技能分析与转型路径
- 🌤️ 天气查询：实时天气信息
- 👔 穿搭建议：结合天气和命理的穿搭推荐

### Q5: 如何集成到我的应用中？

**A**: 启动 HTTP 服务后，可以通过以下方式集成：

**方式1：调用 API**
```bash
curl -X POST http://localhost:8000/api/stream \
  -H "Content-Type: application/json" \
  -d '{
    "type": "query",
    "session_id": "session-123",
    "local_msg_id": "msg-123",
    "content": {
      "query": {
        "prompt": [{
          "type": "text",
          "content": {"text": "你好，请帮我分析今天的运势"}
        }]
      }
    }
  }'
```

**方式2：使用 WebSocket（流式输出）**
```javascript
const eventSource = new EventSource('http://localhost:8000/stream_run');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

## 📊 API 使用方式对比

| 特性 | HTTP 服务 | 命令行测试 | API 集成 |
|------|-----------|-----------|----------|
| 使用难度 | ⭐ 简单 | ⭐⭐ 中等 | ⭐⭐⭐ 高级 |
| 界面 | 有Web界面 | 无界面 | 需自行开发 |
| 流式输出 | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| 集成难度 | 无需集成 | 无需集成 | 需要编写代码 |
| 适用场景 | 直接使用 | 开发测试 | 应用集成 |

## 📝 开发指南

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 加载环境变量
source scripts/load_env.sh

# 启动 HTTP 服务
bash scripts/http_run.sh -p 8000
```

### 运行测试

```bash
# 运行完整测试
bash scripts/local_run.sh -m agent

# 运行单元测试
python test_agent.py
```

## ⚠️ 注意事项

1. **环境变量**：确保已正确设置环境变量（见 `scripts/load_env.sh`）
2. **模型配置**：确保 `config/agent_llm_config.json` 中的模型配置正确
3. **外部 API**：部分功能依赖外部 API（如天气查询），请确保网络连接正常
4. **数据持久化**：默认使用内存存储，重启后对话历史会丢失

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
