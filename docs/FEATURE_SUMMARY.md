# 职场情绪充电站 - 功能使用说明

## 📋 回答你的6个问题

### 1. ✅ 玄学API接入（支持降级）

**实现方式**：
- 创建了 `src/tools/external_api_tool.py`
- 支持外部八字API和紫微斗数API调用
- **自动降级机制**：如果外部API调用失败或超出限制，自动切换到联网搜索模式

**配置方式**：
编辑 `config/external_apis.json`：
```json
{
  "bazi_api": {
    "enabled": true,  // 设置为true启用
    "url": "你的八字API地址",
    "api_key": "你的API密钥"
  }
}
```

**支持的API**：
- 腾讯云市场八字API（100次/天免费）
- 江阴雨辰互联紫微斗数API
- 其他符合格式的第三方API

---

### 2. ✅ MBTI分析（用户直接提供类型）

**实现方式**：
- 创建了 `src/tools/mbti_tool.py`
- 用户直接提供MBTI类型（如：INTJ）
- Agent结合互联网资料进行分析
- 与命理信息交叉验证

**使用示例**：
```
用户：我的MBTI类型是INTJ
Agent：调用mbti_analysis工具，生成详细报告
```

**分析内容**：
- MBTI类型解读
- 性格优劣势
- 适合职业
- 与五行元素交叉验证
- 与职场信息匹配度分析

---

### 3. ✅ 运势趋势图生成（无需额外操作）

**实现方式**：
- 创建了 `src/tools/chart_tool.py`
- 使用 **QuickChart 免费API** 生成图表
- **无需安装任何依赖**，开箱即用

**使用示例**：
```
用户：帮我生成2024年的运势趋势图
Agent：自动调用工具生成图表图片
```

**图表类型**：
- 月度运势趋势线图
- 命理与职场运势对比图
- 雷达图（多维度分析）

---

### 4. ℹ️ Supabase使用说明

**重要**：Supabase 是云服务，不需要本地安装！

**使用步骤**：
1. 访问 [supabase.com](https://supabase.com) 注册
2. 创建项目（免费）
3. 获取 Project URL 和 API Key
4. 创建数据库表（已提供SQL脚本）
5. 配置 `config/supabase_config.json`

**详细指南**：
请查看 `docs/SUPABASE_GUIDE.md`

**免费额度**：
- 500MB 数据库存储
- 50,000 API请求/月
- 1GB 带宽/月

---

### 5. ✅ 紫微斗数深度分析

**实现方式**：
- 创建了 `src/tools/external_api_tool.py` 中的 `ziwei_analysis` 工具
- 支持外部API和联网搜索两种模式
- 自动降级机制

**使用示例**：
```
用户：我想了解我的紫微斗数命盘
Agent：调用ziwei_analysis工具生成报告
```

**配置方式**：
在 `config/external_apis.json` 中配置：
```json
{
  "ziwei_api": {
    "enabled": true,
    "url": "你的紫微斗数API地址",
    "api_key": "你的API密钥"
  }
}
```

---

### 6. ✅ 人际关系建议 & 职业转型建议

**实现方式**：
- 创建了 `src/tools/relationship_tool.py`（人际关系）
- 创建了 `src/tools/career_transition_tool.py`（职业转型）
- 两种方式都可以直接使用，**无需额外操作**

**使用示例**：

**人际关系建议**：
```
用户：我和上司的沟通有些问题
Agent：调用relationship_advice工具，提供解决方案
```

**职业转型建议**：
```
用户：我想从互联网转到金融科技
Agent：调用career_transition_advice工具，提供转型方案
```

**功能特点**：
- 结合MBTI类型提供个性化建议
- 结合五行元素交叉验证
- 提供具体行动方案
- 风险评估和时间规划

---

## 🎯 所有工具清单

| 工具名称 | 文件位置 | 功能说明 | 外部依赖 |
|---------|---------|---------|---------|
| bazi_api_analysis | external_api_tool.py | 八字命理分析 | 外部API（可选）|
| ziwei_analysis | external_api_tool.py | 紫微斗数分析 | 外部API（可选）|
| career_advice | numerology_tool.py | 职场建议 | 联网搜索 |
| get_weather | weather_tool.py | 天气查询 | 联网搜索 |
| dressing_advice | weather_tool.py | 穿搭建议 | 联网搜索 |
| mbti_analysis | mbti_tool.py | MBTI性格分析 | 联网搜索 |
| validate_mbti_with_info | mbti_tool.py | MBTI与信息验证 | 无 |
| generate_luck_chart | chart_tool.py | 运势趋势图生成 | QuickChart（免费）|
| predict_monthly_luck | chart_tool.py | 预测月度运势 | 无 |
| generate_combined_chart | chart_tool.py | 综合趋势图 | QuickChart（免费）|
| relationship_advice | relationship_tool.py | 人际关系建议 | 联网搜索 |
| conflict_resolution | relationship_tool.py | 冲突解决建议 | 联网搜索 |
| career_transition_advice | career_transition_tool.py | 职业转型建议 | 联网搜索 |
| skill_gap_analysis | career_transition_tool.py | 技能差距分析 | 联网搜索 |

---

## 🚀 使用场景示例

### 场景1：首次使用
```
用户：你好，我是产品经理
Agent：🌟 欢迎来到职场情绪充电站！请告诉我你的信息...
用户：我叫小明，男，1990年3月15日8时出生，MBTI是INTJ，在北京，互联网行业，产品经理，P7
Agent：生成完整报告（我的人生解读、每日运势、职场大势、每日穿搭）
```

### 场景2：MBTI分析
```
用户：我的MBTI类型是INTJ，想了解我的性格特点
Agent：调用mbti_analysis工具，生成详细报告
```

### 场景3：运势趋势图
```
用户：帮我生成2024年的运势趋势图
Agent：调用generate_luck_chart工具，生成图表图片
```

### 场景4：人际关系建议
```
用户：我和上司的沟通有些问题
Agent：调用relationship_advice工具，提供解决方案
```

### 场景5：职业转型
```
用户：我想从互联网转到金融科技
Agent：调用career_transition_advice工具，提供转型方案
```

### 场景6：紫微斗数分析
```
用户：我想了解我的紫微斗数命盘
Agent：调用ziwei_analysis工具，生成紫微斗数报告
```

---

## ⚠️ 重要提醒

1. **外部API配置**：
   - 八字和紫微斗数API需要用户提供API Key
   - 如果未配置，自动降级到联网搜索
   - API有免费额度限制（如100次/天）

2. **数据安全**：
   - 用户敏感信息（出生日期等）建议加密存储
   - 如果使用Supabase，启用Row Level Security (RLS)

3. **免责声明**：
   - 所有命理分析**仅供娱乐参考**
   - 实际决策请结合现实情况

---

## 📝 配置文件说明

### config/agent_llm_config.json
- Agent的系统提示词
- 模型配置（使用deepseek-r1-250528）
- 工具列表

### config/external_apis.json
- 外部API配置
- 八字API和紫微斗数API的URL和密钥

### config/supabase_config.json（可选）
- Supabase数据库配置
- URL和API Key

---

## 🎉 总结

所有功能都已实现并测试通过！

✅ **可以直接使用**（无需额外操作）：
- MBTI分析
- 运势趋势图生成
- 人际关系建议
- 职业转型建议
- 紫微斗数分析（降级到联网搜索）

⚙️ **需要配置**（可选）：
- 外部八字API（提升精度）
- 外部紫微斗数API（提升精度）
- Supabase数据库（存储历史记录）

🎯 **核心优势**：
1. 所有功能都有降级方案，确保可用性
2. 结合MBTI、命理、心理学多维度分析
3. 实时联网搜索获取最新信息
4. 生成可视化图表（运势趋势图）
5. 个性化建议（结合用户MBTI和五行）

有任何问题随时问我！
