# Supabase 使用指南

## 什么是 Supabase？

Supabase 是一个开源的 Firebase 替代品，提供：
- PostgreSQL 数据库
- 实时订阅
- 身份认证
- 文件存储
- Edge 函数

**重要：Supabase 是一个云服务，不需要在本地安装！**

## 快速开始

### 1. 注册账户
访问 [supabase.com](https://supabase.com)，免费注册一个账户。

### 2. 创建项目
1. 登录后点击 "New Project"
2. 设置项目名称（如：workplace-emotion-station）
3. 设置数据库密码（请保存好！）
4. 选择区域（建议选择 Asia Northeast - Tokyo，延迟更低）
5. 点击 "Create new project"
6. 等待项目创建完成（通常需要 1-2 分钟）

### 3. 获取 API 凭证
1. 进入项目 Dashboard
2. 点击左侧菜单 "Settings" → "API"
3. 复制以下信息：
   - Project URL
   - anon public key

### 4. 创建数据库表
在 SQL Editor 中执行以下 SQL：

```sql
-- 创建用户咨询记录表
CREATE TABLE user_consultations (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    user_name VARCHAR(100),
    gender VARCHAR(10),
    birth_info JSONB,
    mbti_type VARCHAR(10),
    career_info JSONB,
    report_content TEXT,
    consultation_type VARCHAR(50) DEFAULT 'full_report',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引（提高查询性能）
CREATE INDEX idx_user_consultations_user_id ON user_consultations(user_id);
CREATE INDEX idx_user_consultations_created_at ON user_consultations(created_at DESC);

-- 创建用户档案表（可选）
CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    gender VARCHAR(10),
    birth_info JSONB,
    mbti_type VARCHAR(10),
    career_info JSONB,
    preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 启用行级安全（RLS）
ALTER TABLE user_consultations ENABLE ROW LEVEL SECURITY;

-- 创建策略（示例：允许所有操作，实际使用时应该更严格）
CREATE POLICY "Allow all access" ON user_consultations
    FOR ALL USING (true) WITH CHECK (true);
```

### 5. 配置项目

创建 `config/supabase_config.json` 文件：

```json
{
  "url": "https://your-project.supabase.co",
  "key": "your-anon-public-key",
  "table_consultations": "user_consultations",
  "table_profiles": "user_profiles"
}
```

将你从 Supabase Dashboard 复制的 Project URL 和 anon public key 填入。

### 6. 安装 Python 客户端

在项目中执行：

```bash
pip install supabase
```

### 7. 代码实现示例

创建 `src/storage/supabase_client.py`：

```python
import os
import json
from supabase import create_client, Client
from typing import List, Dict, Any
from datetime import datetime

def get_supabase_client() -> Client:
    """获取 Supabase 客户端"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, "config/supabase_config.json")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return create_client(config['url'], config['key'])

def save_consultation(
    user_id: str,
    user_name: str,
    gender: str,
    birth_info: Dict,
    mbti_type: str,
    career_info: Dict,
    report_content: str,
    consultation_type: str = "full_report"
) -> bool:
    """保存咨询记录"""
    try:
        client = get_supabase_client()
        
        data = {
            "user_id": user_id,
            "user_name": user_name,
            "gender": gender,
            "birth_info": birth_info,
            "mbti_type": mbti_type,
            "career_info": career_info,
            "report_content": report_content,
            "consultation_type": consultation_type,
            "created_at": datetime.now().isoformat()
        }
        
        client.table(config['table_consultations']).insert(data).execute()
        return True
    except Exception as e:
        print(f"保存失败: {str(e)}")
        return False

def get_user_consultations(user_id: str, limit: int = 20) -> List[Dict]:
    """获取用户的咨询记录"""
    try:
        client = get_supabase_client()
        response = client.table(config['table_consultations']) \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return response.data
    except Exception as e:
        print(f"查询失败: {str(e)}")
        return []

def get_growth_trajectory(user_id: str) -> str:
    """生成用户成长轨迹分析"""
    try:
        history = get_user_consultations(user_id, limit=30)
        
        if not history:
            return "暂无历史记录"
        
        trajectory = []
        for i, record in enumerate(history):
            date = record.get('created_at', '')[:10]
            c_type = record.get('consultation_type', 'unknown')
            trajectory.append(f"{i+1}. {date} - {c_type}")
        
        return """📈 你的成长轨迹

{trajectory}

💡 建议持续记录，观察自己的成长变化！
""".format(trajectory="\n".join(trajectory))
    except Exception as e:
        return f"生成轨迹失败: {str(e)}"
```

### 8. 使用 Supabase 工具

创建 `src/tools/history_tool.py`：

```python
from langchain.tools import tool
from storage.supabase_client import save_consultation, get_growth_trajectory

@tool
def save_consultation_record(
    user_id: str,
    user_name: str,
    gender: str,
    birth_info: dict,
    mbti_type: str,
    career_info: dict,
    report_content: str,
    consultation_type: str = "full_report",
    runtime: Any = None
) -> str:
    """保存咨询记录到数据库"""
    if save_consultation(
        user_id, user_name, gender, 
        birth_info, mbti_type, career_info, 
        report_content, consultation_type
    ):
        return "✅ 咨询记录已保存到数据库"
    else:
        return "❌ 保存失败，请稍后再试"

@tool
def get_user_growth_trajectory(user_id: str, runtime: Any = None) -> str:
    """获取用户成长轨迹"""
    return get_growth_trajectory(user_id)
```

## 免费额度

Supabase 免费套餐包含：
- **数据库**：500MB 存储
- **带宽**：1GB/月
- **API 请求**：50,000/月
- **文件存储**：1GB

对于个人项目或小型应用，免费额度完全够用！

## 注意事项

1. **数据安全**：
   - 不要在前端暴露 service_role key
   - 使用 Row Level Security (RLS) 保护数据
   - 定期备份数据

2. **性能优化**：
   - 为常用查询字段创建索引
   - 使用连接池
   - 避免一次性查询大量数据

3. **费用监控**：
   - 定期检查 Dashboard 中的使用量
   - 设置用量警报

## 故障排除

### 连接失败
- 检查 Project URL 和 API Key 是否正确
- 确认网络连接正常
- 检查 Supabase 服务是否在线

### 查询慢
- 检查是否有索引
- 使用 `EXPLAIN` 分析查询计划
- 考虑缓存频繁查询的数据

### 超出配额
- 升级到付费套餐
- 优化数据查询
- 清理旧数据

## 更多资源

- [Supabase 官方文档](https://supabase.com/docs)
- [Supabase Python 客户端](https://supabase.com/docs/reference/python)
- [Supabase 社区](https://supabase.com/docs/guides/community)
