# 访问问题说明与解决方案

## 🔍 问题诊断

你反馈的"打不开链接"可能有以下原因：

### 原因1：这是沙箱环境，无法直接从外部访问

如果你是在Coze平台上使用这个Agent，这是一个**沙箱环境**，意味着：
- ❌ 无法通过浏览器直接访问 http://localhost:8000
- ❌ 无法从你的电脑访问服务器
- ✅ 但Agent功能本身是正常的！

### 原因2：需要正确的访问方式

在不同场景下，访问方式不同：

## ✅ 解决方案

### 方案1：使用命令行测试（推荐，立即可用）

我已为你创建了一个测试脚本 `test_agent.py`，可以立即测试所有功能：

```bash
# 在项目根目录执行
cd /workspace/projects
python test_agent.py
```

这个脚本会自动测试：
- 🔮 命理分析
- 🧠 MBTI分析
- 📈 运势趋势图
- 👥 人际关系
- 💼 职业转型

### 方案2：通过Coze平台界面使用

如果你是在Coze平台上：
1. 在Coze的聊天界面直接输入问题
2. 例如："请帮我分析今天的运势"
3. Agent会正常回复

### 方案3：部署到公网服务器

如果你希望有Web界面供他人使用，需要：

#### 步骤1：准备云服务器
- 购买一台云服务器（阿里云、腾讯云、AWS等）
- 安装Python环境和项目依赖

#### 步骤2：上传项目代码
```bash
# 在云服务器上
git clone <你的项目地址>
cd <项目目录>
pip install -r requirements.txt
```

#### 步骤3：启动服务
```bash
bash scripts/http_run.sh -p 8000
```

#### 步骤4：配置防火墙
确保8000端口开放

#### 步骤5：访问
通过服务器公网IP访问：
```
http://your-server-ip:8000
```

## 🎯 当前环境可用功能

### 1. 命令行测试（立即可用）

运行测试脚本：
```bash
python test_agent.py
```

### 2. 直接调用Agent

```bash
bash scripts/local_run.sh -m agent -i "请帮我分析今天的运势"
```

### 3. 查看服务状态

```bash
# 检查服务是否运行
ps aux | grep "python.*main.py"

# 测试本地访问
curl http://localhost:8000/
```

## 📝 Web界面说明

虽然你现在无法从浏览器访问Web界面，但Web界面已经开发完成，包含：

### 已实现的功能：
- ✅ 醒目的欢迎语和功能介绍
- ✅ 5个功能快捷按钮
- ✅ 实时聊天界面
- ✅ 响应式设计（支持手机）
- ✅ 美观的渐变色UI
- ✅ Markdown格式支持

### 文件位置：
- `src/static/index.html` - 主页面
- `src/static/css/style.css` - 样式
- `src/static/js/app.js` - 交互脚本

## 🚀 如何让Web界面可用

### 选择1：在本地开发环境
如果你有本地的Python环境：
1. 下载项目代码
2. 安装依赖：`pip install -r requirements.txt`
3. 启动服务：`bash scripts/http_run.sh -p 8000`
4. 访问：`http://localhost:8000`

### 选择2：使用Coze平台部署
1. 将代码上传到Coze平台
2. 配置环境变量
3. 启动HTTP服务
4. 获取Coze提供的访问地址

### 选择3：使用容器化部署
```bash
# 构建Docker镜像（需要先创建Dockerfile）
docker build -t workplace-agent .
# 运行容器
docker run -p 8000:8000 workplace-agent
```

## 💡 建议

1. **立即可用**：使用 `python test_agent.py` 测试功能
2. **短期方案**：通过Coze平台界面直接使用
3. **长期方案**：部署到公网服务器，获得完整的Web界面

## 🔧 故障排查

### 如果命令行测试失败：

1. 检查依赖是否安装：
```bash
pip list | grep langchain
```

2. 检查环境变量：
```bash
echo $COZE_WORKLOAD_IDENTITY_API_KEY
echo $COZE_INTEGRATION_MODEL_BASE_URL
```

3. 查看详细日志：
```bash
tail -f /app/work/logs/bypass/app.log
```

## 📞 获取帮助

如果仍然无法访问，请提供以下信息：

1. 你使用的平台（Coze/本地/云服务器）
2. 具体的错误提示
3. 你尝试的访问方式
4. 系统环境信息

---

**最后更新**：2025-01-02
