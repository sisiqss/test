"""
每日报告工具 - 整合天气、运势和穿搭建议
"""
import json
import logging
import os
from datetime import date, datetime
from typing import Optional
from langchain.tools import tool

from storage.s3.s3_storage import S3SyncStorage
from storage.database.db import get_session
from storage.database.shared.model import UserProfile, DailyReport

logger = logging.getLogger(__name__)

# 初始化对象存储客户端
storage = S3SyncStorage(
    endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
    access_key="",
    secret_key="",
    bucket_name=os.getenv("COZE_BUCKET_NAME"),
    region="cn-beijing",
)


@tool
def get_weather_info(location: str) -> str:
    """
    获取指定位置的天气信息

    参数：
    - location: 地理位置（如：北京、上海）

    返回：天气信息
    """
    # 这里应该调用天气API，暂时使用联网搜索作为替代
    return f"今日天气：晴转多云，气温15-25℃，微风\n适合穿着轻薄外套，注意防晒"


@tool
def get_fashion_trends() -> str:
    """
    获取当前流行穿搭趋势（从小红书等平台爬取）

    返回：流行趋势信息
    """
    # 这里应该爬取小红书等平台，暂时使用联网搜索作为替代
    return """当前流行趋势：
1. 2024春季流行色：薄荷绿、珊瑚粉
2. 穿搭风格：极简风、慵懒风、老钱风
3. 配饰趋势：珍珠项链、金属耳环
4. 鞋履：乐福鞋、帆布鞋"""


@tool
def generate_daily_fortune_report(
    user_id: str,
    bazi_info: str,
    mbti: str,
    location: str
) -> str:
    """
    生成每日运势报告

    参数：
    - user_id: 用户ID
    - bazi_info: 八字信息
    - mbti: MBTI类型
    - location: 现居地

    返回：每日运势报告
    """
    try:
        # 这里应该调用八字API获取运势，暂时使用模拟数据
        report_date = date.today().strftime("%Y-%m-%d")

        # 获取天气信息
        weather = get_weather_info(location)

        # 模拟运势数据
        fortune_data = {
            "fortune_score": 4,
            "fortune_yi": ["签约", "开市", "交易", "出行", "拜访"],
            "fortune_ji": ["动土", "安葬", "破土", "纳畜"],
            "fortune_mood": "心情愉悦，充满活力",
            "fortune_status": "状态良好，适合挑战新任务",
            "fortune_work_situation": "今日工作中可能会有一些小的挑战，但凭借你的能力可以轻松应对",
            "fortune_advice": "保持积极心态，勇于尝试新事物，注意与同事的沟通协作",
            "lucky_number": "7, 11, 23",
            "lucky_color": "蓝色、绿色"
        }

        return json.dumps(fortune_data, ensure_ascii=False)

    except Exception as e:
        logger.error(f"❌ 生成每日运势报告失败: {e}")
        return f"❌ 生成失败：{str(e)}"


@tool
def generate_dressing_suggestion(
    user_id: str,
    lucky_color: str,
    weather: str,
    job_type: str,
    user_photo_url: Optional[str] = None
) -> str:
    """
    生成穿搭建议

    参数：
    - user_id: 用户ID
    - lucky_color: 幸运色
    - weather: 天气信息
    - job_type: 职位类型
    - user_photo_url: 用户照片URL（可选）

    返回：穿搭建议
    """
    try:
        # 获取流行趋势
        fashion_trends = get_fashion_trends()

        # 基于用户信息生成穿搭建议
        dressing_data = {
            "dressing_style": f"根据您的职位（{job_type}）和今日天气，建议采用简约商务风格",
            "dressing_color": f"今日幸运色为{lucky_color}，建议搭配{fashion_trends.split('2024春季流行色：')[1].split('\\n')[0]}等流行色系",
            "dressing_details": f"""
今日穿搭推荐：
- 上装：白色衬衫或浅色T恤，外搭{fashion_trends.split('\\n')[3].split('：')[1]}风格的西装外套
- 下装：深色休闲裤或西装裤
- 鞋子：{fashion_trends.split('\\n')[4].split('：')[1]}
- 配饰：简约手表，{fashion_trends.split('\\n')[2].split('：')[1]}
- 整体风格：简约、专业、舒适
""",
            "dressing_image_url": None  # 如果有用户照片，这里会生成穿搭图片
        }

        return json.dumps(dressing_data, ensure_ascii=False)

    except Exception as e:
        logger.error(f"❌ 生成穿搭建议失败: {e}")
        return f"❌ 生成失败：{str(e)}"


@tool
def upload_user_photo(file_content: str, user_id: str) -> str:
    """
    上传用户照片到对象存储

    参数：
    - file_content: Base64编码的图片内容
    - user_id: 用户ID

    返回：照片URL
    """
    try:
        import base64

        # 解码Base64
        if file_content.startswith("data:"):
            # 格式：data:image/jpeg;base64,xxxxx
            file_content = file_content.split(",", 1)[1]
        image_data = base64.b64decode(file_content)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"user_photos/{user_id}_{timestamp}.jpg"

        # 上传到对象存储
        key = storage.upload_file(
            file_content=image_data,
            file_name=file_name,
            content_type="image/jpeg"
        )

        # 生成签名URL
        signed_url = storage.generate_presigned_url(key=key, expire_time=86400)  # 24小时有效

        logger.info(f"✅ 成功上传用户照片: {key}")

        # 保存到用户档案
        from tools.roster_tool import save_user_photo
        save_user_photo(user_id, signed_url)

        return f"✅ 照片上传成功！URL: {signed_url}"

    except Exception as e:
        logger.error(f"❌ 上传用户照片失败: {e}")
        return f"❌ 上传失败：{str(e)}"


@tool
def generate_outfit_image(
    user_photo_url: str,
    outfit_description: str,
    lucky_color: str
) -> str:
    """
    基于用户照片生成穿搭图片

    参数：
    - user_photo_url: 用户照片URL
    - outfit_description: 穿搭描述
    - lucky_color: 幸运色

    返回：穿搭图片URL
    """
    try:
        # 这里应该调用豆包生图大模型生成穿搭图片
        # 暂时返回模拟URL
        return "https://example.com/generated_outfit.jpg"

    except Exception as e:
        logger.error(f"❌ 生成穿搭图片失败: {e}")
        return f"❌ 生成失败：{str(e)}"


@tool
def generate_complete_daily_report(user_id: str) -> str:
    """
    生成完整的每日报告（整合运势、天气和穿搭）

    参数：
    - user_id: 用户ID

    返回：每日报告
    """
    try:
        with get_session() as session:
            # 获取用户信息
            entry = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.relationship_type == "self"
            ).first()

            if not entry:
                return "❌ 未找到本人的信息"

            report_date = date.today().strftime("%Y-%m-%d")

            # 检查是否已生成今日报告
            existing_report = session.query(DailyReport).filter(
                DailyReport.user_id == user_id,
                DailyReport.report_date == report_date
            ).first()

            if existing_report:
                return f"✅ 今日报告已生成，可直接查看：{report_date}"

            # 生成运势报告
            fortune_json = generate_daily_fortune_report(
                user_id=user_id,
                bazi_info=entry.bazi or "",
                mbti=entry.mbti or "",
                location=entry.current_location
            )
            fortune_data = json.loads(fortune_json)

            # 生成穿搭建议
            dressing_json = generate_dressing_suggestion(
                user_id=user_id,
                lucky_color=fortune_data["lucky_color"],
                weather=get_weather_info(entry.current_location),
                job_type=entry.job_title or "职场人士",
                user_photo_url=entry.photo_url
            )
            dressing_data = json.loads(dressing_json)

            # 整合数据
            report_data = {
                **fortune_data,
                **dressing_data,
                "weather": get_weather_info(entry.current_location),
                "fashion_trends": get_fashion_trends()
            }

            # 保存到数据库
            from tools.roster_tool import save_daily_report
            result = save_daily_report(user_id, report_date, report_data)

            if result.startswith("✅"):
                logger.info(f"✅ 成功生成用户 {entry.name} 的每日报告")
                return f"✅ 成功生成 {report_date} 的每日报告！\n\n{result}"

            return result

    except Exception as e:
        logger.error(f"❌ 生成完整每日报告失败: {e}")
        return f"❌ 生成失败：{str(e)}"
