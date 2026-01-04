# 🚀 Render 部署指南 - 职场情绪充电站 API

## 📋 前置要求

- GitHub 账号
- Render 账号（[render.com](https://render.com/)）
- 项目代码完整（包含 `src/`、`config/`、`tools/` 等目录）

---

## 🔧 步骤 1：准备项目代码

### 1.1 检查项目结构

确保你的项目包含以下文件和目录：

```
/workspace/projects/
├── src/
│   ├── agents/
│   │   └── agent.py
│   ├── tools/
│   │   ├── auth_tool.py
│   │   ├── database_tool.py
│   │   └── ... (其他工具)
│   └── storage/
│       └── memory/
│           └── memory_saver.py
├── config/
│   └── agent_llm_config.json
├── backend_api_render.py          # Render 版本的后端 API
├── render.yaml                    # Render 配置文件
└── requirements.txt               # Python 依赖
```

### 1.2 更新 requirements.txt

确保 `requirements.txt` 包含以下依赖：

```txt
flask>=2.0.0
flask-cors>=3.0.0
langchain>=0.1.0
langchain-openai>=0.0.5
langgraph>=0.0.20
requests>=2.28.0
python-dotenv>=0.19.0
```

### 1.3 确认配置文件

检查 `config/agent_llm_config.json` 是否存在且格式正确：

```json
{
    "config": {
        "model": "doubao-seed-1-6-251015",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_completion_tokens": 10000,
        "timeout": 600,
        "thinking": "disabled"
    },
    "sp": "你是职场情绪充电站 AI 助手...",
    "tools": []
}
```

---

## 🌐 步骤 2：创建 GitHub 仓库

### 2.1 初始化 Git 仓库

在项目根目录执行：

```bash
cd /workspace/projects

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Workplace Emotion API"
```

### 2.2 创建 GitHub 仓库

1. 访问 [GitHub](https://github.com/) 并登录
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - Repository name: `workplace-emotion-api`（或其他名称）
   - Description: 职场情绪充电站 API 服务
   - Public/Private: 选择 Private（推荐）
4. 点击 "Create repository"

### 2.3 推送代码到 GitHub

按照 GitHub 页面显示的命令执行：

```bash
# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/workplace-emotion-api.git

# 推送代码
git branch -M main
git push -u origin main
```

---

## 🚀 步骤 3：在 Render 创建 Web Service

### 3.1 登录 Render

1. 访问 [Render](https://dashboard.render.com/)
2. 使用 GitHub 账号登录
3. 授权 Render 访问你的 GitHub 仓库

### 3.2 创建新的 Web Service

1. 点击 "New +" 按钮
2. 选择 "Web Service"

### 3.3 配置 Web Service

#### 3.3.1 连接 GitHub 仓库

1. 在 "Connect" 选项卡下
2. 选择你的 GitHub 账号
3. 找到并选择 `workplace-emotion-api` 仓库
4. 点击 "Connect"

#### 3.3.2 配置构建和部署

填写以下信息：

**Name**（服务名称）：
```
workplace-emotion-api
```

**Region**（区域）：
```
Singapore (推荐，国内访问快)
```

**Branch**（分支）：
```
main
```

**Runtime**（运行环境）：
```
Python 3
```

**Build Command**（构建命令）：
```
pip install -r requirements.txt
```

**Start Command**（启动命令）：
```
python backend_api_render.py
```

#### 3.3.3 实例类型

选择 **Free**（免费版）：
- ✅ 750 小时/月（够用了）
- ✅ 自动 HTTPS
- ✅ 自动域名
- ⚠️ 15 分钟无访问会休眠

### 3.4 配置环境变量（重要！）

点击 "Advanced" → "Add Environment Variable"，逐个添加以下变量：

#### 必需的环境变量

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `COZE_WORKSPACE_PATH` | `/opt/render/project/src` | 工作目录（Render 根目录） |
| `PYTHONPATH` | `/opt/render/project/src:/opt/render/project` | Python 路径 |
| `PORT` | `10000` | Render 默认端口 |

#### 可选的环境变量

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `DEBUG` | `False` | 调试模式（生产环境建议 False） |
| `HOST` | `0.0.0.0` | 监听主机 |

**重要提示**：以下环境变量由 Coze 平台自动提供，**不需要配置**：
- `COZE_WORKLOAD_IDENTITY_API_KEY`
- `COZE_INTEGRATION_MODEL_BASE_URL`

---

## ✅ 步骤 4：部署

### 4.1 开始部署

1. 检查所有配置无误
2. 点击页面底部的 "Create Web Service"
3. Render 会自动开始部署

### 4.2 查看部署日志

1. 在 Web Service 页面点击 "Logs"
2. 查看实时部署日志
3. 等待部署完成（首次部署需要 5-10 分钟）

### 4.3 部署成功的标志

日志中应该看到：

```
🚀 Agent API 服务启动 (Render)
============================================================
🌐 监听主机: 0.0.0.0:10000
📊 健康检查: /api/health
🔧 Agent 聊天: /api/agent/chat
🛠️ 工具列表: /api/tools
🐛 调试模式: False
============================================================
```

---

## 🧪 步骤 5：测试部署

### 5.1 获取服务地址

部署成功后，Render 会提供一个 URL，格式为：

```
https://workplace-emotion-api.onrender.com
```

### 5.2 健康检查

```bash
curl https://workplace-emotion-api.onrender.com/api/health
```

期望返回：

```json
{
  "status": "ok",
  "message": "Agent API 服务正常运行",
  "timestamp": "..."
}
```

### 5.3 测试工具调用

```bash
curl -X POST https://workplace-emotion-api.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "login",
    "tool_params": {
      "username": "admin",
      "password": "admin"
    },
    "user_id": "admin"
  }'
```

期望返回：

```json
{
  "status": "success",
  "data": "✅ 登录成功...",
  "tool_name": "login"
}
```

---

## 🔗 步骤 6：配置 Coze 外部 API 工具

### 6.1 在 Coze 平台添加外部 API 工具

1. 登录 [Coze](https://www.coze.cn/)
2. 进入你的 Agent 编辑页面
3. 点击"插件/工具" → "添加工具" → "外部 API"

### 6.2 配置工具参数

**工具名称**：`database_tool`

**请求 URL**：
```
https://workplace-emotion-api.onrender.com/api/agent/chat
```

**请求方法**：`POST`

**请求头**：
```json
{
  "Content-Type": "application/json"
}
```

**请求参数**（JSON Schema）：
```json
{
  "type": "object",
  "properties": {
    "tool_name": {
      "type": "string",
      "description": "工具名称",
      "enum": [
        "login",
        "register",
        "get_user_info",
        "reset_password",
        "query_contacts",
        "add_contact",
        "query_user_reports",
        "save_report",
        "update_user_profile"
      ]
    },
    "tool_params": {
      "type": "object",
      "description": "工具参数",
      "properties": {}
    },
    "user_id": {
      "type": "string",
      "description": "用户ID"
    }
  },
  "required": ["tool_name", "user_id"]
}
```

### 6.3 配置 Agent 提示词

在 Coze Agent 的提示词中添加：

```
当用户需要以下操作时，请调用 database_tool 工具：

1. 用户登录/注册 → tool_name = "login" 或 "register"
2. 查询用户信息 → tool_name = "get_user_info"
3. 查询联系人列表 → tool_name = "query_contacts"
4. 添加联系人 → tool_name = "add_contact"
5. 查询/保存报告 → tool_name = "query_user_reports" 或 "save_report"
```

---

## 📊 步骤 7：监控和维护

### 7.1 查看日志

在 Render Dashboard：
1. 点击你的 Web Service
2. 点击 "Logs" 标签
3. 实时查看应用日志

### 7.2 手动重新部署

如果你更新了代码：

```bash
# 提交代码
git add .
git commit -m "Update code"
git push origin main
```

Render 会自动检测到更新并重新部署。

### 7.3 查看环境变量

在 Render Dashboard：
1. 点击你的 Web Service
2. 点击 "Environment" 标签
3. 可以查看和修改环境变量

---

## ⚠️ 常见问题

### 1. 部署失败：ModuleNotFoundError

**错误信息**：
```
ModuleNotFoundError: No module named 'src'
```

**解决方案**：
确保配置了 `PYTHONPATH` 环境变量：
```
PYTHONPATH=/opt/render/project/src:/opt/render/project
```

### 2. 部署失败：Agent 构建失败

**错误信息**：
```
❌ Agent 构建失败
```

**解决方案**：
1. 检查 `config/agent_llm_config.json` 是否存在
2. 检查 `src/agents/agent.py` 是否存在
3. 查看 Render 日志了解详细错误

### 3. 工具调用失败：TOOL_NOT_FOUND

**错误信息**：
```json
{
  "status": "failed",
  "error_code": "TOOL_NOT_FOUND",
  "error_message": "工具不存在: xxx"
}
```

**解决方案**：
1. 检查工具名称是否正确
2. 访问 `/api/tools` 查看可用工具列表
3. 确保工具在 `src/tools/` 目录中

### 4. 免费版休眠问题

**现象**：
首次访问需要 30-60 秒启动时间

**解决方案**：
这是 Render 免费版的正常行为。如果需要 24/7 在线，可以升级到付费版（$7/月起）。

### 5. CORS 错误

**错误信息**：
```
Access to fetch at ... has been blocked by CORS policy
```

**解决方案**：
`backend_api_render.py` 已配置 CORS，确保请求头包含 `Content-Type: application/json`

---

## 📝 环境变量总结

### 必需配置

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `COZE_WORKSPACE_PATH` | `/opt/render/project/src` | 工作目录 |
| `PYTHONPATH` | `/opt/render/project/src:/opt/render/project` | Python 路径 |
| `PORT` | `10000` | 端口（Render 自动提供） |

### 可选配置

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `DEBUG` | `False` | 调试模式 |
| `HOST` | `0.0.0.0` | 监听主机 |

---

## 🎉 完成！

部署完成后，你的 API 服务地址为：

```
https://workplace-emotion-api.onrender.com
```

### 可用端点

- **健康检查**：`/api/health`
- **工具列表**：`/api/tools`
- **Agent 聊天**：`/api/agent/chat`

### 在 Coze 平台使用

在 Coze 配置外部 API 工具时，使用以下地址：

```
https://workplace-emotion-api.onrender.com/api/agent/chat
```

---

**🎊 恭喜！你的服务已经成功部署到 Render，Coze Agent 现在可以调用数据库功能了！**
