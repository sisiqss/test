# Agent API 使用指南

## 📋 问题诊断

你遇到的错误 `"terminating connection due to administrator command"` 是因为：

### ❌ 原因：前端直接调用了 Coze API

前端当前调用的是：
```
https://wdssb8q7gh.coze.site/stream_run  ❌ 错误！
```

这会导致连接被 Coze 平台强制终止。

### ✅ 正确方式：前端调用后端 API

前端应该调用：
```
http://localhost:5000/api/agent/chat  ✅ 正确！
```

---

## 🚀 快速开始

### 1. 启动后端服务

```bash
# 安装依赖
pip install flask flask-cors

# 启动服务
cd /workspace/projects
python backend_api.py
```

服务将在 `http://localhost:5000` 启动。

### 2. 测试 API

#### 方式1：使用测试页面（推荐）

打开浏览器访问：
```
http://localhost:5000
```

点击"运行所有测试"按钮，查看所有功能的测试结果。

#### 方式2：使用 curl 测试

```bash
# 1. 健康检查
curl http://localhost:5000/api/health

# 2. 用户登录
curl -X POST http://localhost:5000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "login",
    "tool_params": {
      "username": "admin",
      "password": "admin"
    },
    "user_id": "admin",
    "message": "登录"
  }'

# 3. 查询用户信息
curl -X POST http://localhost:5000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "query_user_by_id",
    "tool_params": {
      "user_id": "admin"
    },
    "user_id": "admin",
    "message": "查询用户信息"
  }'

# 4. 添加联系人
curl -X POST http://localhost:5000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "add_contact",
    "tool_params": {
      "user_id": "admin",
      "contact_data": "{\"name\":\"测试\",\"gender\":\"男\",\"relationship_type\":\"colleague\",\"current_location\":\"北京\"}"
    },
    "user_id": "admin",
    "message": "添加联系人"
  }'

# 5. 获取每日运势和穿搭
curl -X POST http://localhost:5000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_daily_fortune_and_outfit",
    "tool_params": {
      "user_id": "admin",
      "report_date": "2025-01-03"
    },
    "user_id": "admin",
    "message": "获取每日运势和穿搭"
  }'

# 6. 获取工具列表
curl http://localhost:5000/api/tools
```

#### 方式3：使用 JavaScript 调用

参考 `frontend_example.js` 文件中的示例代码。

---

## 📊 API 端点

### 1. 健康检查

```
GET /api/health
```

**响应：**
```json
{
  "status": "ok",
  "message": "Agent API 服务正常运行",
  "timestamp": "..."
}
```

### 2. Agent 聊天（统一接口）

```
POST /api/agent/chat
```

**请求格式：**
```json
{
  "message": "用户消息",
  "user_id": "用户ID（必需）",
  "tool_name": "工具名称（可选，直接调用工具）",
  "tool_params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**成功响应：**
```json
{
  "status": "success",
  "data": "工具返回的数据",
  "tool_name": "工具名称"
}
```

**错误响应：**
```json
{
  "status": "failed",
  "error_code": "ERROR_CODE",
  "error_message": "错误描述"
}
```

### 3. 获取工具列表

```
GET /api/tools
```

**响应：**
```json
{
  "status": "success",
  "total": 50,
  "tools": [
    {
      "name": "login",
      "description": "用户登录验证...",
      "parameters": {...}
    }
  ]
}
```

---

## 🛠️ 可用工具列表

### 用户认证
- `login` - 用户登录
- `register` - 用户注册
- `check_admin` - 检查管理员权限
- `get_user_info` - 获取用户信息
- `reset_password` - 重置密码

### 数据库操作
- `query_user_by_id` - 查询用户信息
- `query_contacts` - 查询联系人列表
- `query_user_reports` - 查询用户报告
- `update_user_profile` - 更新用户档案
- `add_contact` - 添加联系人
- `save_report` - 保存报告

### 花名册管理
- `add_roster_entry` - 添加花名册条目
- `get_roster_entries` - 获取花名册列表
- `update_roster_entry` - 更新花名册条目
- `delete_roster_entry` - 删除花名册条目
- `search_roster_entries` - 搜索花名册条目

### 命理分析
- `bazi_api_analysis` - 八字分析
- `ziwei_analysis` - 紫微斗数分析
- `get_daily_fortune_and_outfit` - 获取每日运势和穿搭（推荐）

### 报告管理
- `save_life_interpretation` - 保存人生解读报告
- `get_life_interpretation` - 获取人生解读报告
- `save_career_trend` - 保存职场大势报告
- `get_career_trend` - 获取职场大势报告
- `save_daily_report` - 保存每日报告
- `get_daily_report` - 获取每日报告

### 消耗管理
- `check_global_usage_limit` - 检查全局消耗限制
- `check_user_usage_limit` - 检查用户消耗限制
- `record_usage` - 记录消耗
- `get_usage_statistics` - 获取消耗统计
- `check_all_limits` - 综合检查所有限制

---

## 💡 使用建议

### 1. 前端代码调整

**错误方式（不要这样做）：**
```javascript
// ❌ 错误！不要直接调用 Coze API
const response = await fetch('https://wdssb8q7gh.coze.site/stream_run', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});
```

**正确方式：**
```javascript
// ✅ 正确！调用后端 API
const response = await fetch('http://localhost:5000/api/agent/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    tool_name: 'login',
    tool_params: {
      username: 'admin',
      password: 'admin'
    },
    user_id: 'admin',
    message: '登录'
  })
});
```

### 2. 每日运势和穿搭

推荐使用合并工具 `get_daily_fortune_and_outfit`，一次获取运势和穿搭：

```javascript
const response = await fetch('http://localhost:5000/api/agent/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    tool_name: 'get_daily_fortune_and_outfit',
    tool_params: {
      user_id: userId,
      report_date: '2025-01-03'
    },
    user_id: userId
  })
});
```

### 3. 资源点消耗

数据库操作**不会消耗资源点**，只有以下操作会消耗：

- 外部 API 调用（八字分析、紫微斗数等）
- 大模型生成（Agent 回复）

### 4. 管理员账户

默认管理员账户：
- 用户名：`admin`
- 密码：`admin`
- 管理员**无消耗限制**

---

## 🐛 故障排除

### 问题1：连接被拒绝

**错误：** `Connection refused`

**解决方案：**
1. 确认后端服务已启动：`ps aux | grep backend_api`
2. 检查端口是否被占用：`lsof -i :5000`
3. 确认防火墙未阻止端口 5000

### 问题2：认证失败

**错误：** `Unauthorized` 或 `认证服务不可用`

**解决方案：**
1. 确认调用的是 `localhost:5000`，不是 Coze API
2. 检查后端日志：`tail -f logs/backend.log`
3. 确认用户名和密码正确

### 问题3：工具调用失败

**错误：** `Tool execution failed`

**解决方案：**
1. 检查工具参数是否正确
2. 查看后端日志获取详细错误信息
3. 确认数据库连接正常

### 问题4：超时

**错误：** `Request timeout`

**解决方案：**
1. 增加超时时间（后端配置）
2. 检查网络连接
3. 确认数据库响应正常

---

## 📞 支持

如果遇到问题，请提供：
1. 完整的错误日志
2. 请求和响应数据
3. 后端日志输出
4. 浏览器控制台错误

---

## ✅ 测试清单

- [ ] 后端服务启动成功
- [ ] 健康检查通过
- [ ] 登录功能正常
- [ ] 查询用户信息正常
- [ ] 添加联系人正常
- [ ] 查询联系人列表正常
- [ ] 获取每日运势和穿搭正常
- [ ] 消耗统计正常
- [ ] 普通对话正常

---

**问题已解决！前端请直接调用 `http://localhost:5000/api/agent/chat`。** 🎉
