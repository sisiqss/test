# 花名册功能实现文档

## 概述

已成功实现花名册功能，包括数据库存储、工具函数和HTTP API接口。

## 1. 数据库表结构

### 1.1 UserProfile（用户信息表）
存储用户及其社交关系信息。

**字段**：
- `id` (主键)
- `user_id` (所属用户ID)
- `name` (姓名，必须)
- `gender` (性别，必须)
- `relationship_type` (关系类型，必须：本人/同事/父母/儿女/朋友/其他)
- `relationship_level` (关系级别，可选：+2/+1/0/-1/-2，仅用于同事)
- `birth_date` (出生年月日时间，本人必须，其他人可选)
- `bazi` (八字，系统产出)
- `mbti` (MBTI类型，可选)
- `birth_place` (出生地，可选)
- `current_location` (现居地，必须)
- `notes` (备注信息，可选)
- `created_at` (创建时间)
- `updated_at` (更新时间)

### 1.2 UserConversationMemory（用户沟通记忆表）
存储用户与Agent的重要对话内容。

**字段**：
- `id` (主键)
- `user_id` (用户ID)
- `contact_user_id` (关联花名册中的联系人ID)
- `conversation_type` (对话类型)
- `content` (对话内容摘要)
- `important_info` (重要信息提取，JSON格式)
- `sentiment` (情感倾向)
- `tags` (标签列表)
- `created_at` (创建时间)
- `updated_at` (更新时间)

## 2. 工具函数

提供了7个LangChain工具函数供Agent使用：

### 2.1 `add_roster_entry`
添加花名册条目。

**必填字段**：
- user_id
- name
- gender
- relationship_type
- current_location

**可选字段**：
- birth_date (本人必须)
- mbti
- birth_place
- relationship_level (仅同事需要)
- notes

### 2.2 `get_roster_entries`
获取花名册列表，支持按关系类型筛选。

### 2.3 `get_roster_entry_by_id`
根据ID获取花名册条目详情。

### 2.4 `update_roster_entry`
更新花名册条目。

### 2.5 `delete_roster_entry`
删除花名册条目。

### 2.6 `search_roster_entries`
搜索花名册条目（支持姓名、MBTI、备注）。

### 2.7 `add_user_bazi`
为用户添加八字信息。

## 3. HTTP API接口

提供了8个REST API接口：

### 3.1 POST /api/roster
添加花名册条目。

**请求体**：
```json
{
  "user_id": "user-123",
  "name": "张三",
  "gender": "男",
  "relationship_type": "本人",
  "current_location": "北京",
  "birth_date": "1990年03月15日08时",
  "mbti": "INTJ",
  "birth_place": "上海",
  "notes": "互联网产品经理"
}
```

### 3.2 GET /api/roster
获取花名册列表。

**查询参数**：
- user_id (必须)
- relationship_type (可选)

**示例**：
```
GET /api/roster?user_id=user-123&relationship_type=同事
```

### 3.3 GET /api/roster/{entry_id}
获取花名册条目详情。

### 3.4 PUT /api/roster/{entry_id}
更新花名册条目。

### 3.5 DELETE /api/roster/{entry_id}
删除花名册条目。

### 3.6 GET /api/roster/search
搜索花名册条目。

**查询参数**：
- user_id (必须)
- keyword (必须)

**示例**：
```
GET /api/roster/search?user_id=user-123&keyword=产品经理
```

### 3.7 POST /api/roster/bazi
为用户添加八字信息。

**请求体**：
```json
{
  "user_id": "user-123",
  "bazi": "庚午年己卯月乙酉日辛巳时"
}
```

## 4. System Prompt更新

更新了System Prompt，集成花名册功能：

1. **首次使用必须录入本人信息到花名册**
2. **在生成命理分析报告后，调用 `add_user_bazi` 保存八字信息**
3. **支持添加其他联系人（同事、父母、儿女、朋友等）**
4. **同事可以标注关系级别（+2/+1/0/-1/-2）**
5. **在对话中如果发现重要信息，主动询问用户是否保存到花名册**

## 5. 使用示例

### 示例1：首次使用Agent
```
用户：你好，我想使用这个Agent
Agent：🌟 欢迎来到职场情绪充电站！🌟
      我是你的专属职场导师...
      为了给你提供最贴心的个性化服务，请告诉我以下信息...
用户：我叫张三，男，1990年3月15日8点出生，INTJ，现在在北京
Agent：✅ 我已经将你的信息保存到花名册中了！
      现在让我为你生成一份完整的报告...
```

### 示例2：添加同事
```
用户：帮我添加我的同事李四的信息，她是我的上级，ENFP
Agent：好的，我来帮你添加李四的信息。请问她的现居地是哪里？
用户：上海
Agent：✅ 添加成功！李四（同事 +1）已添加到你的花名册
```

### 示例3：查看花名册
```
用户：查看我的花名册
Agent：📋 你的花名册（共2条）：
      **张三** - 本人
      **李四** - 同事 (+1)
      ...
```

## 6. 测试结果

所有功能测试通过：

✅ 数据库表创建成功
✅ 添加花名册条目（本人、同事、朋友）
✅ 获取花名册列表
✅ 按关系类型筛选
✅ 搜索花名册
✅ 更新花名册条目
✅ 删除花名册条目
✅ 添加八字信息

## 7. 关键特性

1. **关系类型丰富**：支持本人、同事、父母、儿女、朋友、其他6种关系
2. **同事关系细化**：支持+2/+1/0/-1/-2五个级别，代表上下级和平级关系
3. **八字自动保存**：Agent在生成八字分析后，自动保存到花名册
4. **灵活查询**：支持按关系类型筛选、按关键词搜索
5. **完整CRUD**：支持增删改查全部操作

## 8. 注意事项

1. user_id使用session_id作为唯一标识
2. 本人信息中出生年月日时间为必填字段
3. 关系级别仅用于同事类型
4. 所有命理分析仅供娱乐参考
5. 数据库表已创建在PostgreSQL中

## 9. 后续扩展

可以进一步实现：
1. 用户沟通记忆的自动记录和检索
2. 基于花名册信息的个性化推荐
3. 关系图谱可视化
4. 批量导入/导出花名册
5. 用户权限管理
