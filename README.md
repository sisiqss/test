# 职场情绪充电站 AI Agent

一个基于Coze平台的职场情绪充电站AI Agent，集成命理分析、职场咨询、情绪支持和实用建议功能。

## ✨ 功能特性

- 🔮 **命理分析**：八字、紫微斗数运势分析
- 🧠 **MBTI分析**：性格分析与职场建议
- 📈 **运势趋势图**：可视化运势变化趋势
- 👥 **人际关系**：性格匹配与沟通建议
- 💼 **职业转型**：可迁移技能分析与转型路径

## 🚀 快速开始

### ⭐ 方式一：直接使用 Coze Web 界面（推荐！立即可用）

**无需任何配置，直接访问即可使用所有功能！**

👉 访问地址：**https://wdssb8q7gh.coze.site/**

#### 为什么推荐？
- ✅ 无需任何配置
- ✅ 无需发布到API通道
- ✅ 无需Token
- ✅ 立即可用
- ✅ 功能完整

#### 如何使用：
1. 打开浏览器，访问 `https://wdssb8q7gh.coze.site/`
2. 在聊天框中发送任意消息
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

### 方式二：本地运行（开发者）

```bash
# 测试Agent
bash scripts/local_run.sh -m agent
```

---

### 方式三：使用自定义前端（需要配置）

**注意**：此方式需要将Bot发布到API通道。

#### 前置条件：
1. Bot已发布到"Agent as API"通道
2. 已获取API Token

#### 配置步骤：

1. **发布Bot到API通道**
   - 登录 https://www.coze.cn/
   - 进入Bot配置页面
   - 点击"发布"，选择"Agent as API"通道
   - 等待1-2分钟生效

2. **启动本地服务**
   ```bash
   bash scripts/http_run.sh -p 8000
   ```

3. **访问前端**
   ```
   http://localhost:8000
   ```

详细步骤请参考：[Bot发布到API通道完整指南](docs/BOT_SETUP_GUIDE.md)

---

## 📚 详细文档

### 使用指南
- [Bot发布到API通道指南](docs/BOT_SETUP_GUIDE.md) - 如何发布Bot到API通道
- [Coze平台使用指南](docs/COZE_PLATFORM_GUIDE.md) - Coze平台的使用方法
- [分享使用指南](docs/SHARING_GUIDE.md) - 如何分享给他人使用
- [API Token配置说明](docs/API_TOKEN_FAQ.md) - Token配置相关问题
- [访问问题说明](docs/ACCESS_ISSUES.md) - 解决访问问题

### 功能文档
- [功能总结](docs/FEATURE_SUMMARY.md) - 完整功能说明
- [Supabase配置](docs/SUPABASE_GUIDE.md) - 云端数据库配置

## 🎯 项目结构

```
.
├── config                   # 配置文件
│   ├── agent_llm_config.json  # 模型配置
│   └── external_apis.json      # 外部API配置
├── docs                      # 文档
│   ├── BOT_SETUP_GUIDE.md     # Bot发布指南
│   ├── COZE_PLATFORM_GUIDE.md  # Coze平台指南
│   ├── API_TOKEN_FAQ.md       # Token配置FAQ
│   ├── ACCESS_ISSUES.md       # 访问问题说明
│   ├── SHARING_GUIDE.md       # 分享指南
│   ├── FEATURE_SUMMARY.md    # 功能总结
│   └── SUPABASE_GUIDE.md     # Supabase配置
├── src                       # 源代码
│   ├── agents                 # Agent代码
│   │   └── agent.py           # 主Agent
│   ├── tools                  # 工具代码
│   │   ├── external_api_tool.py
│   │   ├── mbti_tool.py
│   │   ├── chart_tool.py
│   │   ├── relationship_tool.py
│   │   └── career_transition_tool.py
│   ├── static                 # 前端资源（需Bot发布到API通道后才可用）
│   │   ├── index.html
│   │   ├── css/style.css
│   │   └── js/app.js
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

- **平台**：Coze平台
- **框架**：LangChain, LangGraph
- **模型**：deepseek-r1-250528
- **前端**：原生HTML/CSS/JavaScript
- **数据可视化**：QuickChart API
- **搜索**：联网搜索集成

## 🤔 常见问题

### Q1: 我应该使用哪种方式？

**A**: 
- **90%的情况**：直接访问 `https://wdssb8q7gh.coze.site/`（推荐）
- **10%的情况**：如果你是开发者，需要集成到自己的应用，才需要发布Bot到API通道

### Q2: 为什么前端页面调用API报错？

**A**: 因为Bot没有发布到API通道。有两个解决方案：

**方案1（推荐）**：
直接使用Coze平台的Web界面：`https://wdssb8q7gh.coze.site/`

**方案2**：
发布Bot到API通道，详细步骤见 [Bot发布指南](docs/BOT_SETUP_GUIDE.md)

### Q3: 什么是Bot？什么是API通道？

**A**:
- **Bot**：你在Coze平台创建的AI智能体
- **API通道**：让Bot可以通过API被调用的发布通道

详细说明见 [Bot发布指南](docs/BOT_SETUP_GUIDE.md)

### Q4: 我需要配置API Token吗？

**A**:
- **使用Coze Web界面**：不需要
- **通过API调用Bot**：需要

详细说明见 [API Token FAQ](docs/API_TOKEN_FAQ.md)

### Q5: 如何分享给其他人？

**A**: 直接分享这个链接：
```
https://wdssb8q7gh.coze.site/
```

接收者无需任何配置，点击即可使用！

## 📊 使用方式对比

| 特性 | Coze Web界面 | 自定义前端 | 命令行测试 |
|------|-------------|-----------|-----------|
| 使用难度 | ⭐ 简单 | ⭐⭐⭐ 中等 | ⭐⭐ 中等 |
| 配置复杂度 | 无需配置 | 需要发布API通道 | 无需配置 |
| 自定义界面 | 固定界面 | 完全自定义 | 无界面 |
| 立即可用 | ✅ 是 | ❌ 需要配置 | ✅ 是 |
| 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 💡 建议

### 对于普通用户：
1. **直接访问** `https://wdssb8q7gh.coze.site/`
2. 开始使用所有功能
3. 无需任何配置

### 对于开发者：
1. 先试用Coze Web界面，确认功能满足需求
2. 如果需要集成到自己的应用，参考 [Bot发布指南](docs/BOT_SETUP_GUIDE.md)
3. 发布Bot到API通道
4. 使用API调用Bot

## 🎉 开始使用

**立即访问**：
```
https://wdssb8q7gh.coze.site/
```

**开始体验职场情绪充电站的所有功能！** 🚀

---

**最后更新**：2025-01-02
**版本**：1.0.0
