# 职场情绪充电站 AI Agent

一个基于Coze平台的职场情绪充电站AI Agent，集成命理分析、职场咨询、情绪支持和实用建议功能。

## ✨ 功能特性

- 🔮 **命理分析**：八字、紫微斗数运势分析
- 🧠 **MBTI分析**：性格分析与职场建议
- 📈 **运势趋势图**：可视化运势变化趋势
- 👥 **人际关系**：性格匹配与沟通建议
- 💼 **职业转型**：可迁移技能分析与转型路径

## 🚀 快速开始

### 方式一：Web界面访问（推荐）

启动HTTP服务后，直接在浏览器访问即可：

```bash
# 启动服务（默认端口8000）
bash scripts/http_run.sh -p 8000
```

然后打开浏览器访问：`http://localhost:8000`

Web界面特性：
- ✅ 醒目的欢迎语和功能介绍
- ✅ 5个快捷功能按钮，一键触发
- ✅ 精美的聊天界面，支持实时对话
- ✅ 响应式设计，支持手机访问

### 方式二：命令行测试

```bash
# 测试Agent
bash scripts/local_run.sh -m agent
```

## 📚 详细文档

- [分享使用指南](docs/SHARING_GUIDE.md) - 如何分享给他人使用
- [功能总结](docs/FEATURE_SUMMARY.md) - 完整功能说明
- [Supabase配置](docs/SUPABASE_GUIDE.md) - 云端数据库配置

## 🎯 项目结构

# 本地运行
## 运行流程
bash scripts/local_run.sh -m flow

## 运行节点
bash scripts/local_run.sh -m node -n node_name

# 启动HTTP服务
bash scripts/http_run.sh -p 8000

## 📁 前端资源

- `src/static/index.html` - Web前端主页面
- `src/static/css/style.css` - 样式文件
- `src/static/js/app.js` - 交互脚本

## ⚙️ 配置说明

所有配置文件位于 `config/` 目录：
- `agent_llm_config.json` - 模型配置
- `external_apis.json` - 外部API配置

## 🛠️ 技术栈

- **平台**：Coze平台
- **框架**：LangChain, LangGraph
- **模型**：deepseek-r1-250528
- **前端**：原生HTML/CSS/JavaScript
- **数据可视化**：QuickChart API
- **搜索**：联网搜索集成


