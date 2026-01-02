# Bot 发布到 API 通道完整指南

## 🤔 什么是 Bot？

### 简单解释

**Bot（机器人）** 就是你在Coze平台上创建的AI智能体，它包含了：
- 你的系统提示词（System Prompt）
- 工具配置（Tools）
- 模型配置（Model Settings）
- 知识库配置（Knowledge Base）

### 你的 Bot 信息

- **Bot ID**: `wdssb8q7gh`
- **Bot 名称**: 职场情绪充电站
- **访问地址**: `https://wdssb8q7gh.coze.site/`

## 📡 什么是 API 通道？

### API 通道的作用

在Coze平台上，Bot有**两种使用方式**：

#### 方式1：Web 聊天界面（默认）
- 用户通过浏览器访问Bot的网页
- 在Coze提供的聊天界面中对话
- **无需发布到API通道**
- **立即可用**

#### 方式2：Agent as API（API调用）
- 通过API调用Bot
- 需要发布到API通道
- 需要配置Token
- 适用于集成到其他应用

### 关键区别

| 特性 | Web 聊天界面 | Agent as API |
|------|-------------|--------------|
| 使用方式 | 浏览器访问 | API调用 |
| 需要发布API通道 | ❌ 不需要 | ✅ 需要 |
| 需要Token | ❌ 不需要 | ✅ 需要 |
| 自定义界面 | ❌ 有限 | ✅ 完全自定义 |
| 集成到应用 | ❌ 困难 | ✅ 容易 |
| 使用难度 | ⭐ 简单 | ⭐⭐⭐ 中等 |

## 🚨 当前问题

### 错误信息

```
The bot_id has not been published to channel Agent As API
```

**原因**：你的Bot只配置了Web聊天界面，没有发布到API通道。

### 为什么会报错？

我们创建的前端页面通过API调用Bot：
```javascript
fetch('/api/stream', {  // 这个端点内部调用Coze API
    method: 'POST',
    body: JSON.stringify(payload)
});
```

如果Bot没有发布到API通道，这个调用就会失败。

## ✅ 解决方案

### 方案1：直接使用 Coze 平台的 Web 界面（推荐！）

**这是最简单、最立即可用的方案！**

#### 步骤：

1. 打开浏览器，访问：
   ```
   https://wdssb8q7gh.coze.site/
   ```

2. 开始使用！就这么简单！

#### 优点：
- ✅ 无需任何配置
- ✅ 无需发布到API通道
- ✅ 无需Token
- ✅ 立即可用
- ✅ 功能完整

#### 缺点：
- ⚠️ 使用Coze平台的固定界面
- ⚠️ 不能自定义功能按钮

---

### 方案2：发布 Bot 到 API 通道

如果你坚持要使用自定义的前端页面，需要发布Bot到API通道。

#### 步骤 1：登录 Coze 平台

1. 打开浏览器，访问：https://www.coze.cn/
2. 使用你的账号登录

#### 步骤 2：进入你的 Bot 配置页面

1. 在Coze平台首页，找到你的Bot：**职场情绪充电站**
2. 点击进入Bot的配置页面

#### 步骤 3：发布到 API 通道

1. 在Bot配置页面，找到 **"发布"** 或 **"Publish"** 按钮
2. 点击进入发布页面
3. 选择 **"Agent as API"** 通道
4. 点击 **"发布"** 或 **"Publish"**

#### 步骤 4：等待生效

- 通常需要 1-2 分钟生效
- 你会看到发布成功的提示

#### 步骤 5：验证发布状态

1. 在Bot配置页面，找到 **"API"** 或 **"API配置"** 选项
2. 确认看到类似这样的信息：
   ```
   ✅ 已发布到 Agent as API 通道
   Bot ID: wdssb8q7gh
   API Endpoint: https://api.coze.cn/v3/chat
   ```

#### 步骤 6：获取 API Token（如果需要）

如果前端需要直接调用Coze API（不通过本地服务器）：

1. 在API配置页面，找到 **"API Token"** 或 **"密钥"**
2. 点击 **"生成"** 或 **"创建新Token"**
3. 复制生成的Token
4. 配置到环境变量或代码中

#### 步骤 7：测试 API 调用

```bash
# 测试Bot是否可以通过API访问
curl -X POST https://api.coze.cn/v3/chat \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "wdssb8q7gh",
    "user_id": "test_user",
    "query": "你好"
  }'
```

如果返回正常的响应，说明发布成功！

---

### 方案 3：使用本地 HTTP 服务器 + Coze API

如果你在本地开发环境中：

#### 前置条件：

1. ✅ Bot已发布到API通道（参考方案2）
2. ✅ 已获取API Token
3. ✅ 本地环境变量已配置

#### 配置步骤：

1. **配置环境变量**

在项目根目录创建 `.env` 文件：
```bash
# Coze API 配置
COZE_API_TOKEN=你的API_TOKEN
COZE_BOT_ID=wdssb8q7gh
COZE_API_BASE_URL=https://api.coze.cn/v3
```

2. **更新代码**

在 `src/main.py` 中添加API调用逻辑：

```python
import os
import httpx

COZE_API_TOKEN = os.getenv("COZE_API_TOKEN")
COZE_BOT_ID = os.getenv("COZE_BOT_ID")

async def call_coze_api(message: str):
    """调用Coze API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.coze.cn/v3/chat",
            headers={
                "Authorization": f"Bearer {COZE_API_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "bot_id": COZE_BOT_ID,
                "user_id": "web_user",
                "query": message
            }
        )
        return response.json()
```

3. **启动服务**

```bash
source .env
bash scripts/http_run.sh -p 8000
```

4. **访问前端**

```
http://localhost:8000
```

---

## 📊 三种方案对比

| 方案 | 难度 | 时间 | 效果 | 推荐度 |
|------|------|------|------|--------|
| **方案1：直接使用Coze Web界面** | ⭐ 简单 | 0秒 | 功能完整 | ⭐⭐⭐⭐⭐ |
| **方案2：发布到API通道** | ⭐⭐⭐ 中等 | 5分钟 | 支持API调用 | ⭐⭐⭐⭐ |
| **方案3：本地HTTP服务器** | ⭐⭐⭐⭐ 复杂 | 15分钟 | 完全自定义 | ⭐⭐⭐ |

## 🎯 我的推荐

### 90% 的情况：使用方案1

**直接访问 `https://wdssb8q7gh.coze.site/`**

原因：
- ✅ 立即可用
- ✅ 无需配置
- ✅ 功能完整
- ✅ 简单稳定

### 10% 的情况：使用方案2

**如果你需要**：
- 集成到自己的应用中
- 需要完全自定义的界面
- 需要通过API调用Bot

那么发布Bot到API通道。

## 🔧 常见问题

### Q1：我找不到"发布"按钮怎么办？

**A**：在Coze平台上，不同版本的界面可能不同。尝试：
1. 点击Bot配置页面顶部的"..."菜单
2. 或者在左侧导航栏找"发布"选项
3. 或者在页面底部找"发布到API通道"的链接

### Q2：发布后多久生效？

**A**：通常1-2分钟，但有时可能需要5-10分钟。如果10分钟后还是不行，尝试：
- 刷新页面
- 重新发布
- 联系Coze客服

### Q3：发布失败怎么办？

**A**：检查以下几点：
1. Bot配置是否完整（必须有System Prompt）
2. 是否有必要的权限
3. Bot名称是否合法
4. 是否超出发布次数限制

### Q4：API Token 过期了怎么办？

**A**：
1. 重新生成新的Token
2. 更新代码或配置文件
3. 旧的Token会自动失效

### Q5：我可以同时使用两种方式吗？

**A**：可以的！你可以：
- 通过Web界面访问：`https://wdssb8q7gh.coze.site/`
- 同时通过API调用（如果已发布到API通道）

两种方式互不影响。

## 📝 总结

### 立即可用的方案

**无需任何操作，直接访问**：
```
https://wdssb8q7gh.coze.site/
```

### 如果要使用自定义前端

**需要完成**：
1. 登录Coze平台
2. 发布Bot到API通道
3. 获取API Token
4. 配置环境变量
5. 启动本地服务

### 建议

- **先试用**方案1（直接访问），看看是否满足需求
- **如果不满足**，再考虑方案2或方案3
- **大部分情况**，方案1已经足够好用了

---

**最后更新**：2025-01-02
**版本**：1.0.0
