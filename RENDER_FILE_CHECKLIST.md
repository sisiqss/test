# ✅ Render 部署文件清单

## 📦 需要上传到 GitHub 的文件

### 核心文件（必需）

- [ ] `backend_api_render.py` - Render 版本的后端 API
- [ ] `render.yaml` - Render 配置文件
- [ ] `requirements.txt` - Python 依赖列表
- [ ] `config/agent_llm_config.json` - Agent 配置

### 源码目录（必需）

- [ ] `src/agents/agent.py` - Agent 构建代码
- [ ] `src/tools/` - 工具目录
  - [ ] `src/tools/auth_tool.py` - 认证工具
  - [ ] `src/tools/database_tool.py` - 数据库工具
  - [ ] `src/tools/daily_fortune_outfit_tool.py` - 每日运势工具
  - [ ] `src/tools/mbti_tool.py` - MBTI 工具
  - [ ] `src/tools/numerology_tool.py` - 数理工具
  - [ ] `src/tools/chart_tool.py` - 图表工具
  - [ ] `src/tools/relationship_tool.py` - 关系工具
  - [ ] `src/tools/career_transition_tool.py` - 职业转型工具
  - [ ] `src/tools/roster_tool.py` - 花名册工具
  - [ ] `src/tools/quick_report_tool.py` - 快速报告工具
  - [ ] `src/tools/usage_limit_tool.py` - 消耗限制工具
- [ ] `src/storage/memory/memory_saver.py` - 记忆保存器

### 文档文件（可选）

- [ ] `RENDER_DEPLOYMENT.md` - Render 部署指南
- [ ] `RENDER_ENV_VARS.md` - 环境变量配置

---

## 🚀 部署前检查

### 1. 检查文件完整性

在项目根目录执行：

```bash
# 检查核心文件是否存在
ls -la backend_api_render.py
ls -la render.yaml
ls -la requirements.txt
ls -la config/agent_llm_config.json

# 检查源码目录
ls -la src/agents/agent.py
ls -la src/tools/
ls -la src/storage/memory/memory_saver.py
```

### 2. 检查 requirements.txt

确保包含以下依赖：

```txt
flask>=2.0.0
flask-cors>=3.0.0
langchain>=0.1.0
langchain-openai>=0.0.5
langgraph>=0.0.20
requests>=2.28.0
python-dotenv>=0.19.0
```

检查命令：

```bash
cat requirements.txt
```

### 3. 检查配置文件

```bash
cat config/agent_llm_config.json
```

应该看到：

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

## 📋 Git 提交命令

### 1. 初始化 Git 仓库

```bash
cd /workspace/projects

# 初始化
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Workplace Emotion API for Render"
```

### 2. 推送到 GitHub

```bash
# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/workplace-emotion-api.git

# 推送代码
git branch -M main
git push -u origin main
```

---

## 🧪 本地测试（可选）

在推送到 GitHub 前，可以本地测试：

```bash
# 设置环境变量
export COZE_WORKSPACE_PATH=/workspace/projects/src
export PYTHONPATH=/workspace/projects/src:/workspace/projects

# 运行服务
python backend_api_render.py

# 在另一个终端测试
curl http://localhost:10000/api/health
```

---

## ✅ 完成检查清单

- [ ] 所有必需文件已创建
- [ ] `requirements.txt` 包含所有依赖
- [ ] `config/agent_llm_config.json` 格式正确
- [ ] `src/` 目录完整
- [ ] 已初始化 Git 仓库
- [ ] 已提交代码
- [ ] 已推送到 GitHub
- [ ] 可以在 GitHub 上看到所有文件

---

**检查无误后，按照 RENDER_DEPLOYMENT.md 开始部署到 Render！** 🚀
