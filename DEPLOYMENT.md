# 🚀 职场情绪充电站 - 部署指南

## 📋 目录

1. [部署前准备](#部署前准备)
2. [快速部署](#快速部署)
3. [手动部署](#手动部署)
4. [前端配置](#前端配置)
5. [常见问题](#常见问题)

---

## 📦 部署前准备

### 1. 服务器要求

- **操作系统**: Linux（推荐 Ubuntu 20.04+）
- **Python**: 3.8+
- **内存**: 2GB+
- **磁盘**: 10GB+
- **端口**: 5000（可修改）

### 2. 依赖检查

```bash
# 检查 Python 版本
python --version

# 检查 pip
pip --version
```

### 3. 域名准备

确保你有一个可以访问的域名，例如：
- `https://your-domain.com`
- `https://api.your-domain.com`

---

## ⚡ 快速部署

### 步骤1：克隆项目

```bash
cd /workspace/projects
```

### 步骤2：配置环境变量

编辑 `.env.production` 文件：

```bash
vi .env.production
```

修改以下配置：

```bash
# API 服务配置
API_BASE_URL=https://your-domain.com  # 修改为你的域名
API_HOST=0.0.0.0
API_PORT=5000

# 调试模式（生产环境建议关闭）
DEBUG=False
```

### 步骤3：执行部署脚本

```bash
./deploy.sh
```

部署脚本会自动完成：
- ✅ 安装 Python 依赖
- ✅ 检查端口占用
- ✅ 加载环境变量
- ✅ 启动 API 服务
- ✅ 输出服务信息

### 步骤4：验证部署

访问以下地址验证服务：

- **健康检查**: `https://your-domain.com/api/health`
- **测试页面**: `https://your-domain.com/index.html`

---

## 🔧 手动部署

### 步骤1：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤2：配置环境变量

```bash
export API_BASE_URL=https://your-domain.com
export API_HOST=0.0.0.0
export API_PORT=5000
export DEBUG=False
```

### 步骤3：启动服务

**前台运行（测试）**:
```bash
python backend_api.py
```

**后台运行（生产）**:
```bash
nohup python backend_api.py > api.log 2>&1 &
```

### 步骤4：查看日志

```bash
tail -f api.log
```

### 步骤5：停止服务

```bash
# 查找进程
ps aux | grep backend_api.py

# 停止进程（替换 PID）
kill <PID>
```

---

## 🌐 前端配置

### 方式1：环境变量配置（推荐）

在部署前端时，注入环境变量：

```javascript
// 使用 window.API_BASE_URL
const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000';
```

部署示例：

```html
<!-- 在 index.html 中注入 -->
<script>
  window.API_BASE_URL = 'https://your-domain.com';
</script>
```

### 方式2：配置文件

创建 `config.js`：

```javascript
// config.js
const API_BASE_URL = 'https://your-domain.com';
```

在 HTML 中引用：

```html
<script src="config.js"></script>
```

### 方式3：运行时配置

使用 `index.html` 提供的配置区域：

1. 打开测试页面：`https://your-domain.com/index.html`
2. 在 "API 配置" 区域输入你的域名
3. 点击 "更新 API URL"
4. 点击 "测试连接" 验证

### 方式4：localStorage 配置

```javascript
// 在浏览器控制台执行
localStorage.setItem('API_BASE_URL', 'https://your-domain.com');

// 刷新页面
location.reload();
```

---

## 📝 前端调用示例

### 基本配置

```javascript
// 配置 API Base URL
const API_BASE_URL = 'https://your-domain.com';

// 或从环境变量读取
const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000';

// 或从 localStorage 读取
const API_BASE_URL = localStorage.getItem('API_BASE_URL') || 'http://localhost:5000';
```

### 调用示例

```javascript
// 登录
async function login(username, password) {
    const response = await fetch(`${API_BASE_URL}/api/agent/chat`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            tool_name: 'login',
            tool_params: {username, password},
            user_id: username
        })
    });

    return await response.json();
}

// 查询用户信息
async function getUserInfo(userId) {
    const response = await fetch(`${API_BASE_URL}/api/agent/chat`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            tool_name: 'get_user_info',
            tool_params: {},
            user_id: userId
        })
    });

    return await response.json();
}
```

### 健康检查

```javascript
// 检查服务状态
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const result = await response.json();

        if (result.status === 'ok') {
            console.log('✅ 服务正常');
        } else {
            console.error('❌ 服务异常');
        }
    } catch (error) {
        console.error('❌ 连接失败:', error);
    }
}
```

---

## 🔍 常见问题

### 1. 前端无法连接后端

**问题**: 访问 `https://your-domain.com` 时提示连接失败

**解决方案**:
1. 检查后端服务是否启动：`ps aux | grep backend_api.py`
2. 检查端口是否开放：`netstat -tuln | grep 5000`
3. 检查防火墙规则
4. 确认 API_BASE_URL 配置正确

### 2. CORS 错误

**问题**: 控制台显示 `Access to fetch at ... from origin ... has been blocked by CORS policy`

**解决方案**:
- 后端已启用 CORS，确认前端配置了正确的 API_BASE_URL

### 3. 端口被占用

**问题**: 启动时提示端口 5000 被占用

**解决方案**:
```bash
# 查找占用进程
lsof -i :5000

# 停止进程
kill -9 <PID>

# 或修改 .env.production 中的 API_PORT
```

### 4. 依赖安装失败

**问题**: `pip install -r requirements.txt` 失败

**解决方案**:
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. 日志查看

```bash
# 实时查看日志
tail -f api.log

# 查看最近 100 行
tail -n 100 api.log

# 查看错误日志
grep ERROR api.log
```

---

## 📊 监控和维护

### 健康检查

定期检查服务状态：

```bash
curl https://your-domain.com/api/health
```

### 日志轮转

使用 logrotate 管理日志：

```bash
sudo vi /etc/logrotate.d/api
```

添加以下内容：

```
/workspace/projects/api.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

### 重启服务

```bash
# 停止服务
ps aux | grep backend_api.py | grep -v grep | awk '{print $2}' | xargs kill

# 启动服务
export $(grep -v '^#' .env.production | xargs)
nohup python backend_api.py > api.log 2>&1 &

# 检查服务
tail -f api.log
```

---

## 📞 技术支持

如有问题，请检查：
1. 日志文件：`api.log`
2. 健康检查：`/api/health`
3. 工具列表：`/api/tools`

---

**部署完成后，访问 `https://your-domain.com/index.html` 进行测试！** 🎉
