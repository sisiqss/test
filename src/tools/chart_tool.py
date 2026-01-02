import json
from langchain.tools import tool
from typing import Any, List


@tool
def generate_luck_chart(monthly_scores: List[int], year: str, name: str, runtime: Any) -> str:
    """
    生成运势趋势图。使用 QuickChart 免费API，无需额外安装。

    Args:
        monthly_scores: 12个月的运势分数（1-100）
        year: 年份（如：2024）
        name: 用户姓名
        runtime: 工具运行时对象
    
    Returns:
        图表Markdown格式，包含图表图片URL
    """
    if len(monthly_scores) != 12:
        return "❌ 错误：必须提供12个月的运势分数"
    
    if not all(1 <= score <= 100 for score in monthly_scores):
        return "❌ 错误：运势分数必须在1-100之间"
    
    # 创建Chart.js配置
    chart_config = {
        "type": "line",
        "data": {
            "labels": ["1月", "2月", "3月", "4月", "5月", "6月", 
                      "7月", "8月", "9月", "10月", "11月", "12月"],
            "datasets": [{
                "label": f"{year}年运势走势",
                "data": monthly_scores,
                "borderColor": "rgb(99, 102, 241)",
                "backgroundColor": "rgba(99, 102, 241, 0.1)",
                "fill": True,
                "tension": 0.4,
                "pointRadius": 5,
                "pointHoverRadius": 7,
                "pointBackgroundColor": "rgb(99, 102, 241)",
                "pointBorderColor": "#fff",
                "pointBorderWidth": 2
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": f"{name} - {year}年运势趋势图",
                    "font": {
                        "size": 18,
                        "weight": "bold"
                    },
                    "color": "#333"
                },
                "legend": {
                    "display": True,
                    "position": "top"
                }
            },
            "scales": {
                "y": {
                    "min": 0,
                    "max": 100,
                    "title": {
                        "display": True,
                        "text": "运势指数"
                    },
                    "grid": {
                        "color": "rgba(0, 0, 0, 0.1)"
                    }
                },
                "x": {
                    "title": {
                        "display": True,
                        "text": "月份"
                    },
                    "grid": {
                        "display": False
                    }
                }
            }
        }
    }
    
    # 使用QuickChart生成图表
    chart_url = f"https://quickchart.io/chart?c={json.dumps(chart_config)}"
    
    # 分析趋势
    avg_score = sum(monthly_scores) / 12
    max_month = monthly_scores.index(max(monthly_scores)) + 1
    min_month = monthly_scores.index(min(monthly_scores)) + 1
    
    trend_analysis = ""
    if monthly_scores[:6] > monthly_scores[6:]:
        trend_analysis = "📈 上半年运势较好，适合把握机会"
    else:
        trend_analysis = "📈 下半年运势上升，可以期待突破"
    
    return f"""📈 {name}的{year}年运势趋势图

![运势趋势]({chart_url})

**图表数据：**
• 平均运势指数：{avg_score:.1f}
• 运势最佳月份：{max_month}月（{max(monthly_scores)}分）
• 运势低谷月份：{min_month}月（{min(monthly_scores)}分）

{trend_analysis}

💡 查看【高清原图】：{chart_url}

📊 **详细数据：**
{chr(10).join([f'{i+1}月: {score}分' for i, score in enumerate(monthly_scores)])}

⚠️ 提醒：以上运势趋势仅供娱乐参考，实际决策请结合现实情况。
"""


@tool
def predict_monthly_luck(birth_year: str, birth_month: str, birth_day: str, 
                         birth_hour: str, gender: str, year: str, runtime: Any) -> str:
    """
    预测一年12个月的运势分数。
    
    Args:
        birth_year, birth_month, birth_day, birth_hour: 出生日期
        gender: 性别
        year: 预测年份
        runtime: 工具运行时对象
    
    Returns:
        月度运势分数JSON字符串
    """
    # 这里使用简化的算法计算月度运势
    # 实际应用中应该调用专业命理API或使用更复杂的算法
    
    base_score = 70  # 基础分数
    
    monthly_scores = []
    for month in range(1, 13):
        # 基于出生信息、月份、性别等因素的简化计算
        # 这是一个示例算法，实际应该使用专业命理方法
        
        # 1. 基础分
        score = base_score
        
        # 2. 基于出生月的影响
        birth_month_int = int(birth_month)
        if month == birth_month_int:
            score += 10  # 出生月加分
        elif abs(month - birth_month_int) == 6:
            score -= 5  # 对冲月减分
        
        # 3. 基于奇偶月的影响（简化）
        if month % 2 == 0:
            score += 3
        else:
            score -= 2
        
        # 4. 基于季节的影响（简化）
        if 3 <= month <= 5:  # 春季
            score += 2
        elif 6 <= month <= 8:  # 夏季
            score -= 1
        elif 9 <= month <= 11:  # 秋季
            score += 3
        else:  # 冬季
            score -= 2
        
        # 5. 确保分数在1-100之间
        score = max(40, min(100, score))
        
        monthly_scores.append(int(score))
    
    return json.dumps({
        "year": year,
        "monthly_scores": monthly_scores,
        "description": "基于简化算法的运势预测，实际应用应使用专业命理API"
    })


@tool
def generate_combined_chart(bazi_scores: List[int], career_scores: List[int], 
                          year: str, name: str, runtime: Any) -> str:
    """
    生成命理运势和职场运势的对比趋势图。
    
    Args:
        bazi_scores: 命理月度分数（12个月）
        career_scores: 职场月度分数（12个月）
        year: 年份
        name: 姓名
        runtime: 工具运行时对象
    
    Returns:
        对比图表
    """
    if len(bazi_scores) != 12 or len(career_scores) != 12:
        return "❌ 错误：必须提供12个月的分数"
    
    chart_config = {
        "type": "line",
        "data": {
            "labels": ["1月", "2月", "3月", "4月", "5月", "6月", 
                      "7月", "8月", "9月", "10月", "11月", "12月"],
            "datasets": [
                {
                    "label": "命理运势",
                    "data": bazi_scores,
                    "borderColor": "rgb(99, 102, 241)",
                    "backgroundColor": "rgba(99, 102, 241, 0.1)",
                    "fill": False,
                    "tension": 0.4
                },
                {
                    "label": "职场运势",
                    "data": career_scores,
                    "borderColor": "rgb(234, 88, 12)",
                    "backgroundColor": "rgba(234, 88, 12, 0.1)",
                    "fill": False,
                    "tension": 0.4
                }
            ]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": f"{name} - {year}年命理与职场运势对比",
                    "font": {
                        "size": 18,
                        "weight": "bold"
                    }
                }
            },
            "scales": {
                "y": {
                    "min": 0,
                    "max": 100
                }
            }
        }
    }
    
    chart_url = f"https://quickchart.io/chart?c={json.dumps(chart_config)}"
    
    return f"""📊 {name}的{year}年运势对比图

![运势对比]({chart_url})

💡 查看【高清原图】：{chart_url}

🔵 蓝色线：命理运势趋势
🟠 橙色线：职场运势趋势

⚠️ 提醒：以上分析仅供参考。
"""
