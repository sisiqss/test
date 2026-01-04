# 📋 Render 环境变量配置

## 快速配置

在 Render 的 Web Service 配置页面，点击 "Advanced" → "Add Environment Variable"，添加以下变量：

---

## 必需的环境变量

### 1. COZE_WORKSPACE_PATH

**Key**: `COZE_WORKSPACE_PATH`
**Value**: `/opt/render/project/src`
**Description**: Coze 工作目录

### 2. PYTHONPATH

**Key**: `PYTHONPATH`
**Value**: `/opt/render/project/src:/opt/render/project`
**Description**: Python 模块搜索路径

### 3. PORT

**Key**: `PORT`
**Value**: `10000`
**Description**: 服务端口（Render 自动提供，但建议显式配置）

---

## 可选的环境变量

### 4. DEBUG

**Key**: `DEBUG`
**Value**: `False`
**Description**: 调试模式（生产环境建议设置为 False）

### 5. HOST

**Key**: `HOST`
**Value**: `0.0.0.0`
**Description**: 监听主机地址

---

## 不需要配置的环境变量

以下环境变量由 Coze 平台在运行时自动注入，**不要手动配置**：

- `COZE_WORKLOAD_IDENTITY_API_KEY` - API 密钥
- `COZE_INTEGRATION_MODEL_BASE_URL` - 模型基础 URL

---

## 配置完成检查清单

配置完成后，确保以下 3 个变量已添加：

- [x] `COZE_WORKSPACE_PATH` = `/opt/render/project/src`
- [x] `PYTHONPATH` = `/opt/render/project/src:/opt/render/project`
- [x] `PORT` = `10000`

---

## 配置示例

在 Render 环境变量配置页面应该看到：

| Key | Value | Type |
|-----|-------|------|
| `COZE_WORKSPACE_PATH` | `/opt/render/project/src` | Text |
| `PYTHONPATH` | `/opt/render/project/src:/opt/render/project` | Text |
| `PORT` | `10000` | Text |
| `DEBUG` | `False` | Text |
| `HOST` | `0.0.0.0` | Text |

---

**配置完成后，点击 "Save Changes" 保存，然后重新部署服务。**
