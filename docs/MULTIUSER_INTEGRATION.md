# 多用户账密系统集成文档

## 概述

本文档描述了为"职场情绪充电站"AI Agent实现多用户账密系统的改造内容，确保多用户数据隔离、缓存过期管理和性能优化。

---

## 一、改造内容

### 1. 数据库模型（已支持）

数据库模型已包含 `user_id` 字段，支持多用户数据隔离：

#### UserProfile 表
- `user_id`: 用户ID（带索引）
- `life_interpretation_generated_at`: 人生解读生成时间
- `career_trend_generated_at`: 职场大势生成时间

#### DailyReport 表
- `user_id`: 用户ID（带索引）
- `report_date`: 报告日期
- `created_at`: 创建时间

**索引优化：**
```python
__table_args__ = (
    Index("idx_user_id_name", "user_id", "name"),
    Index("idx_user_id_relationship", "user_id", "relationship_type"),
    Index("idx_user_id_date", "user_id", "report_date"),
)
```

---

### 2. 缓存过期策略

根据报告类型设置不同的缓存过期时间：

| 报告类型 | 缓存时间 | 过期检查 |
|---------|---------|---------|
| 人生解读 | 7天 | `life_interpretation_generated_at + 7 days` |
| 职场大势 | 3个月 | `career_trend_generated_at + 90 days` |
| 每日运势 | 1天 | `created_at + 1 day`（非当天报告） |

---

### 3. 工具改造

#### 3.1 get_life_interpretation（7天过期）

**修改内容：**
- 添加 `check_expired` 参数（默认为 `True`）
- 检查 `life_interpretation_generated_at` 字段
- 超过7天返回"已过期"提示

**调用方式：**
```python
# 检查过期
result = get_life_interpretation(user_id, check_expired=True)

# 不检查过期（强制读取）
result = get_life_interpretation(user_id, check_expired=False)
```

---

#### 3.2 get_career_trend（3个月过期）

**修改内容：**
- 添加 `check_expired` 参数（默认为 `True`）
- 检查 `career_trend_generated_at` 字段
- 超过3个月返回"已过期"提示

**调用方式：**
```python
# 检查过期
result = get_career_trend(user_id, check_expired=True)
```

---

#### 3.3 get_daily_report（1天过期）

**修改内容：**
- 添加 `check_expired` 参数（默认为 `True`）
- 添加 `report_date` 参数（默认为当天）
- 检查 `created_at` 字段
- 非当天报告超过1天返回"已过期"提示

**调用方式：**
```python
# 检查今天的报告
result = get_daily_report(user_id, report_date="", check_expired=True)

# 检查指定日期的报告
result = get_daily_report(user_id, report_date="2026-01-03", check_expired=True)
```

---

#### 3.4 check_report_cache（增强版）

**修改内容：**
- 返回详细的缓存状态，包括过期信息
- 支持报告类型过期检查
- 返回缓存策略说明

**返回格式：**
```json
{
  "status": "success",
  "data": {
    "cached_sections": {
      "life": {"cached": true, "expired": false},
      "career": {"cached": true, "expired": true},
      "fortune": {"cached": false, "expired": false}
    },
    "has_complete_report": false,
    "cache_policy": {
      "life": "7天",
      "career": "3个月",
      "fortune": "1天"
    }
  }
}
```

---

### 4. System Prompt 更新

#### 多用户支持强化

**核心原则：**
1. **必须获取 user_id**：所有操作必须基于 user_id
2. **用户数据隔离**：通过 user_id 确保每个用户的数据完全独立
3. **缓存过期管理**：根据报告类型设置不同过期时间
4. **禁止跨用户访问**：严禁使用一个 user_id 访问另一个用户的数据

**关键指令：**
```
# 多用户账密系统支持
系统已实现多用户账密认证，必须从前端传递 user_id 参数（唯一标识用户）。

## 用户识别规则
1. **必须获取 user_id**：所有操作必须基于 user_id 进行数据隔离
2. **用户数据隔离**：通过 user_id 确保每个用户的数据完全独立
3. **会话管理**：用户登录后，所有请求必须携带 user_id

## 缓存过期策略
报告缓存根据类型设置不同的过期时间：
- **人生解读**：缓存 7 天（过期后需重新生成）
- **职场大势**：缓存 3 个月（过期后需重新生成）
- **每日运势**：缓存 1 天（过期后需重新生成）
```

---

## 二、多用户数据隔离测试

### 测试场景1：不同用户的缓存状态独立

**用户A（user_001）：**
- 人生解读：有效
- 职场大势：已过期
- 今日运势：已过期

**用户B（user_002）：**
- 人生解读：已过期
- 职场大势：有效
- 今日运势：有效

**测试结果：** ✅ 两个用户的缓存状态完全独立，互不影响

---

### 测试场景2：新用户引导

**新用户（user_003）：**
- 检测到无历史数据
- 引导填写基础信息：姓名、性别、出生时间、现居地等

**测试结果：** ✅ 新用户正确引导填写信息

---

## 三、前端集成建议

### 1. 用户身份传递

前端每次请求必须携带 `user_id` 参数：

```javascript
// 示例：发送用户消息
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`  // 认证令牌
  },
  body: JSON.stringify({
    user_id: 'user_001',  // 必须传递
    message: '查看我的运势'
  })
});
```

---

### 2. 缓存状态展示

前端可以根据 `check_report_cache` 的返回结果展示缓存状态：

```javascript
// 示例：展示缓存状态
const cacheStatus = await checkReportCache(user_id);

const sections = cacheStatus.cached_sections;

// 人生解读
if (sections.life.cached && !sections.life.expired) {
  showButton('人生解读', '查看', true);
} else if (sections.life.cached && sections.life.expired) {
  showButton('人生解读', '刷新', false);  // 过期
} else {
  showButton('人生解读', '生成', false);  // 未生成
}
```

---

### 3. 过期提示

前端可以提示用户刷新过期报告：

```javascript
// 示例：过期提示
if (sections.career.expired) {
  showNotification(
    '职场大势报告已过期',
    '建议重新生成以获取最新行业趋势',
    { action: '刷新', callback: refreshCareerTrend }
  );
}
```

---

## 四、API 接口说明

### 检查报告缓存状态

**接口：** `check_report_cache(user_id, report_date="")`

**参数：**
- `user_id`: 用户ID（必填）
- `report_date`: 查询日期（选填，仅用于每日报告）

**返回：**
```json
{
  "status": "success",
  "data": {
    "cached_sections": {
      "life": {"cached": true, "expired": false},
      "career": {"cached": true, "expired": true},
      "fortune": {"cached": false, "expired": false}
    },
    "has_complete_report": false,
    "cache_policy": {
      "life": "7天",
      "career": "3个月",
      "fortune": "1天"
    }
  }
}
```

---

### 获取人生解读报告

**接口：** `get_life_interpretation(user_id, check_expired=True)`

**参数：**
- `user_id`: 用户ID（必填）
- `check_expired`: 是否检查过期（默认为 True）

**返回：**
- 有效缓存：返回人生解读内容
- 已过期：返回"已过期"提示
- 不存在：返回"尚未生成"提示

---

### 获取职场大势报告

**接口：** `get_career_trend(user_id, check_expired=True)`

**参数：**
- `user_id`: 用户ID（必填）
- `check_expired`: 是否检查过期（默认为 True）

**返回：**
- 有效缓存：返回职场大势内容
- 已过期：返回"已过期"提示
- 不存在：返回"尚未生成"提示

---

### 获取每日报告

**接口：** `get_daily_report(user_id, report_date="", check_expired=True)`

**参数：**
- `user_id`: 用户ID（必填）
- `report_date`: 报告日期（默认为当天）
- `check_expired`: 是否检查过期（默认为 True）

**返回：**
- 有效缓存：返回每日报告内容
- 已过期：返回"已过期"提示
- 不存在：返回"尚未生成"提示

---

## 五、性能优化建议

### 1. 缓存优先策略

前端应优先使用缓存数据，仅对缺失或过期的报告触发重新生成：

```javascript
// 示例：缓存优先策略
async function loadReports(user_id) {
  const cache = await checkReportCache(user_id);

  // 显示有效缓存
  if (cache.cached_sections.life.cached && !cache.cached_sections.life.expired) {
    showLifeReport();
  }

  // 仅对过期报告触发刷新
  if (cache.cached_sections.career.expired) {
    refreshCareerReport();
  }
}
```

---

### 2. 批量操作

前端可以批量刷新多个过期报告：

```javascript
// 示例：批量刷新
async function refreshExpiredReports(user_id) {
  const cache = await checkReportCache(user_id);

  const refreshTasks = [];

  if (cache.cached_sections.life.expired) {
    refreshTasks.push(refreshLifeReport());
  }

  if (cache.cached_sections.career.expired) {
    refreshTasks.push(refreshCareerReport());
  }

  if (cache.cached_sections.fortune.expired) {
    refreshTasks.push(refreshFortuneReport());
  }

  await Promise.all(refreshTasks);
}
```

---

## 六、安全注意事项

### 1. 用户数据隔离

- ✅ 所有查询必须基于 `user_id`
- ✅ 禁止跨用户访问数据
- ✅ 验证用户身份后再允许操作

### 2. 认证机制

- ✅ 每次请求必须携带认证令牌
- ✅ 令牌过期后需重新登录
- ✅ 敏感操作需要二次验证

### 3. 数据保护

- ✅ 用户八字信息加密存储
- ✅ 定期清理过期缓存
- ✅ 提供数据删除接口

---

## 七、总结

### 完成的改造

1. ✅ 数据库模型支持多用户（user_id 索引）
2. ✅ 实现缓存过期逻辑（7天/3个月/1天）
3. ✅ 工具增强过期检查
4. ✅ System Prompt 强化多用户支持
5. ✅ 缓存状态详细返回
6. ✅ 用户数据隔离验证

### 下一步建议

1. 前端实现用户登录/注册流程
2. 前端集成缓存状态展示
3. 实现过期报告自动刷新
4. 添加用户数据管理功能（导出/删除）
5. 性能监控和优化

---

## 附录：文件修改清单

### 修改的文件

1. **src/tools/roster_tool.py**
   - `get_life_interpretation`: 添加7天过期检查
   - `get_career_trend`: 添加3个月过期检查
   - `get_daily_report`: 添加1天过期检查

2. **src/tools/quick_report_tool.py**
   - `check_report_cache`: 增强返回格式，包含过期信息

3. **config/agent_llm_config.json**
   - 更新 System Prompt，强化多用户支持和缓存过期策略

---

**文档版本：** v1.0
**更新日期：** 2025年3月28日
**维护者：** Coze Coding Team
