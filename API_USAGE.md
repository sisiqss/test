# 📚 API 使用指南

## 🎯 核心原则

**请勿调用 Coze API！**

- ❌ `https://wdssb8q7gh.coze.site/stream_run`（Coze 平台）
- ✅ `http://localhost:5000/api/agent/chat`（本地 Agent）

---

## 📍 API Base URL

```javascript
// 开发环境
const API_BASE_URL = 'http://localhost:5000';

// 生产环境
const API_BASE_URL = 'https://your-domain.com';
```

---

## 🔧 方式1：直接调用工具（推荐）

**适用场景**：明确知道要调用哪个工具，性能最好

### 请求格式

```javascript
POST /api/agent/chat
Content-Type: application/json

{
  "tool_name": "login",           // 工具名称（必需）
  "tool_params": {                // 工具参数（必需）
    "username": "admin",
    "password": "admin"
  },
  "user_id": "admin"              // 用户ID（必需）
}
```

### 响应格式

```json
{
  "status": "success",
  "data": {
    "message": "登录成功",
    "user_info": {...}
  },
  "tool_name": "login"
}
```

### 完整示例

```javascript
// 1. 登录
const response = await fetch(`${API_BASE_URL}/api/agent/chat`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    tool_name: 'login',
    tool_params: {
      username: 'admin',
      password: 'admin'
    },
    user_id: 'admin'
  })
});

const result = await response.json();
console.log(result.data);
```

### 可用工具列表

#### 认证工具
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `login` | 用户登录 | `username`, `password` |
| `register` | 用户注册 | `username`, `password`, `name` |
| `get_user_info` | 获取用户信息 | - |
| `reset_password` | 重置密码 | `username`, `new_password` |

#### 数据库工具
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `query_user_by_id` | 查询用户 | - |
| `query_contacts` | 查询联系人列表 | - |
| `query_user_reports` | 查询用户报告 | `report_type` |
| `update_user_profile` | 更新用户资料 | `profile_data` |
| `add_contact` | 添加联系人 | `contact_data` |
| `save_report` | 保存报告 | `report_type`, `report_data` |

#### 业务工具
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `get_daily_fortune_and_outfit` | 每日运势和穿搭 | `query_date` |
| `numerology_analysis` | 数理分析 | `name`, `birth_date` |
| `mbti_analysis` | MBTI 分析 | `mbti_type` |
| `get_usage_statistics` | 消耗统计 | `query_date` |

---

## 💬 方式2：通过 LLM 对话

**适用场景**：不确定用户需求，让 LLM 自动决定调用哪个工具

### 请求格式

```javascript
POST /api/agent/chat
Content-Type: application/json

{
  "message": "帮我登录",              // 用户消息（必需）
  "user_id": "admin"                  // 用户ID（必需）
}
```

### 响应格式

```json
{
  "status": "success",
  "data": {
    "messages": [
      {
        "role": "assistant",
        "content": "登录成功！..."
      }
    ]
  }
}
```

### 完整示例

```javascript
const response = await fetch(`${API_BASE_URL}/api/agent/chat`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: '我想查看今天的运势',
    user_id: 'admin'
  })
});

const result = await response.json();
console.log(result.data.messages[0].content);
```

---

## 📊 健康检查

### 请求

```javascript
GET /api/health
```

### 响应

```json
{
  "status": "ok",
  "message": "Agent API 服务正常运行",
  "timestamp": "2025-01-03 12:00:00"
}
```

---

## 🛠️ 获取工具列表

### 请求

```javascript
GET /api/tools
```

### 响应

```json
{
  "status": "success",
  "total": 15,
  "tools": [
    {
      "name": "login",
      "description": "用户登录工具",
      "parameters": {...}
    }
  ]
}
```

---

## 💡 最佳实践

### 1. 明确需求，使用方式1（直接调用工具）

```javascript
// ✅ 推荐：直接调用工具
fetch(`${API_BASE_URL}/api/agent/chat`, {
  method: 'POST',
  body: JSON.stringify({
    tool_name: 'login',
    tool_params: {username: 'admin', password: 'admin'},
    user_id: 'admin'
  })
});

// ❌ 不推荐：通过 LLM 对话
fetch(`${API_BASE_URL}/api/agent/chat`, {
  method: 'POST',
  body: JSON.stringify({
    message: '帮我登录',
    user_id: 'admin'
  })
});
```

### 2. 不确定需求，使用方式2（通过 LLM）

```javascript
// ✅ 推荐：让 LLM 自动决定
fetch(`${API_BASE_URL}/api/agent/chat`, {
  method: 'POST',
  body: JSON.stringify({
    message: '我感觉最近工作压力大，有什么建议吗？',
    user_id: 'admin'
  })
});
```

### 3. 错误处理

```javascript
async function callAPI(toolName, toolParams, userId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/agent/chat`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        tool_name: toolName,
        tool_params: toolParams,
        user_id: userId
      })
    });

    const result = await response.json();

    if (result.status === 'success') {
      return result.data;
    } else {
      throw new Error(result.error_message);
    }
  } catch (error) {
    console.error('调用失败:', error);
    throw error;
  }
}
```

---

## ⚠️ 常见错误

### 1. 调用 Coze API

**错误示例**：
```javascript
// ❌ 错误：调用 Coze API
fetch('https://wdssb8q7gh.coze.site/stream_run', ...)
```

**正确做法**：
```javascript
// ✅ 正确：调用本地 API
fetch('http://localhost:5000/api/agent/chat', ...)
```

### 2. 缺少 user_id

**错误示例**：
```javascript
// ❌ 错误：缺少 user_id
fetch(`${API_BASE_URL}/api/agent/chat`, {
  method: 'POST',
  body: JSON.stringify({
    tool_name: 'login',
    tool_params: {...}
  })
})
```

**正确做法**：
```javascript
// ✅ 正确：包含 user_id
fetch(`${API_BASE_URL}/api/agent/chat`, {
  method: 'POST',
  body: JSON.stringify({
    tool_name: 'login',
    tool_params: {...},
    user_id: 'admin'
  })
})
```

### 3. 工具名称错误

**错误示例**：
```javascript
// ❌ 错误：工具名称错误
tool_name: 'user_login'
```

**正确做法**：
```javascript
// ✅ 正确：使用正确的工具名称
tool_name: 'login'
```

---

## 📞 技术支持

- 查看 API 文档：`API_USAGE.md`
- 部署文档：`DEPLOYMENT.md`
- 测试页面：`http://localhost:5000/index.html`
