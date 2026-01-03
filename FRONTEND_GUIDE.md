# 🎯 前端对接指南 - 问题解答

## 📋 问题汇总

### 问题1：Coze API 返回自然语言，不调用工具

**现象**：
```json
{
  "message": "由于用户多次要求使用管理员账户登录，我将调用登录工具。"
}
```

**原因**：
- 前端调用了 **Coze 平台 API**：`https://wdssb8q7gh.coze.site/stream_run`
- Coze 平台的 Agent 无法调用你的自定义 Python 工具（数据库、认证等）

---

## ✅ 解决方案

### 核心原则

**请勿调用 Coze API，统一使用本地 Agent！**

| 服务 | 地址 | 状态 | 工具调用 |
|------|------|------|----------|
| ❌ Coze API | `https://wdssb8q7gh.coze.site/stream_run` | 不可用 | 返回自然语言 |
| ✅ 本地 Agent | `http://localhost:5001/api/agent/chat` | 可用 | 真实调用工具 |

---

## 🚀 正确的使用方式

### 步骤1：确认 API 地址

```javascript
// 开发环境
const API_BASE_URL = 'http://localhost:5001';

// 生产环境（部署后）
const API_BASE_URL = 'https://your-domain.com:5001';
```

### 步骤2：直接调用工具（推荐）

```javascript
// 登录示例
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

### 步骤3：处理响应

```javascript
if (result.status === 'success') {
  console.log('工具调用成功:', result.data);
} else {
  console.error('工具调用失败:', result.error_message);
}
```

---

## 📊 API 测试结果

### ✅ 测试通过

```bash
# 1. 健康检查
curl http://localhost:5001/api/health

# 返回：
{
  "status": "ok",
  "message": "Agent API 服务正常运行"
}

# 2. 登录工具
curl -X POST http://localhost:5001/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "login",
    "tool_params": {"username": "admin", "password": "admin"},
    "user_id": "admin"
  }'

# 返回：
{
  "status": "success",
  "data": "✅ 登录成功...",
  "tool_name": "login"
}

# 3. 查询用户信息
curl -X POST http://localhost:5001/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_user_info",
    "tool_params": {},
    "user_id": "admin"
  }'

# 返回：
{
  "status": "success",
  "data": "✅ 用户信息...",
  "tool_name": "get_user_info"
}
```

---

## 🔧 可用工具列表

### 认证工具
- `login` - 用户登录
- `register` - 用户注册
- `get_user_info` - 获取用户信息
- `reset_password` - 重置密码

### 数据库工具
- `query_user_by_id` - 查询用户
- `query_contacts` - 查询联系人列表
- `query_user_reports` - 查询用户报告
- `update_user_profile` - 更新用户资料
- `add_contact` - 添加联系人
- `save_report` - 保存报告

### 业务工具
- `get_daily_fortune_and_outfit` - 每日运势和穿搭
- `numerology_analysis` - 数理分析
- `mbti_analysis` - MBTI 分析
- `get_usage_statistics` - 消耗统计

---

## 💡 常见错误

### ❌ 错误1：调用 Coze API

```javascript
// ❌ 错误
fetch('https://wdssb8q7gh.coze.site/stream_run', ...)
```

**后果**：返回自然语言，不调用工具

**正确做法**：
```javascript
// ✅ 正确
fetch('http://localhost:5001/api/agent/chat', ...)
```

### ❌ 错误2：使用错误的端口

```javascript
// ❌ 错误：端口 5000 被 Coze 服务占用
const API_BASE_URL = 'http://localhost:5000';
```

**正确做法**：
```javascript
// ✅ 正确：使用端口 5001
const API_BASE_URL = 'http://localhost:5001';
```

### ❌ 错误3：缺少 user_id

```javascript
// ❌ 错误：缺少 user_id
fetch(`${API_BASE_URL}/api/agent/chat`, {
  method: 'POST',
  body: JSON.stringify({
    tool_name: 'login',
    tool_params: {username: 'admin', password: 'admin'}
  })
})
```

**后果**：返回 400 错误

**正确做法**：
```javascript
// ✅ 正确：包含 user_id
fetch(`${API_BASE_URL}/api/agent/chat`, {
  method: 'POST',
  body: JSON.stringify({
    tool_name: 'login',
    tool_params: {username: 'admin', password: 'admin'},
    user_id: 'admin'
  })
})
```

---

## 📝 完整示例

### 登录流程

```javascript
async function login(username, password) {
  try {
    const response = await fetch('http://localhost:5001/api/agent/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        tool_name: 'login',
        tool_params: {username, password},
        user_id: username
      })
    });

    const result = await response.json();

    if (result.status === 'success') {
      console.log('登录成功');
      return result.data;
    } else {
      console.error('登录失败:', result.error_message);
      throw new Error(result.error_message);
    }
  } catch (error) {
    console.error('请求失败:', error);
    throw error;
  }
}

// 使用示例
login('admin', 'admin')
  .then(data => console.log(data))
  .catch(error => console.error(error));
```

### 查询联系人

```javascript
async function getContacts(userId) {
  try {
    const response = await fetch('http://localhost:5001/api/agent/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        tool_name: 'query_contacts',
        tool_params: {},
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
    console.error('查询失败:', error);
    throw error;
  }
}
```

---

## 🧪 测试页面

访问测试页面验证功能：

```
http://localhost:5001/index.html
```

测试步骤：
1. 打开测试页面
2. 在 "API 配置" 区域输入：`http://localhost:5001`
3. 点击 "更新 API URL"
4. 点击 "测试连接"（应显示 ✅）
5. 测试各个功能按钮

---

## 📚 参考文档

- [API 使用指南](API_USAGE.md)
- [部署文档](DEPLOYMENT.md)
- [工具列表](http://localhost:5001/api/tools)

---

## ✨ 总结

### 架构说明

```
前端 → 本地 Agent (backend_api.py) → 工具调用 → 数据库/外部API
```

### 关键要点

1. ✅ **统一使用本地 API**：`http://localhost:5001/api/agent/chat`
2. ✅ **直接调用工具**：明确工具时，使用 `tool_name` 参数
3. ✅ **必须包含 user_id**：所有请求都需要用户ID
4. ✅ **错误处理**：检查 `result.status === 'success'`

### 方案对比

| 方案 | 状态 | 说明 |
|------|------|------|
| 选项 A：本地 Agent | ✅ 已实现 | 完全控制工具调用，推荐使用 |
| 选项 B：Coze API | ❌ 不可用 | 无法调用自定义工具 |

---

**现在请前端同事按照以上指南对接，如有问题请随时反馈！** 🚀
