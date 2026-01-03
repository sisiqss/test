"""
花名册功能测试脚本
"""
import logging
import sys

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加src到路径
sys.path.insert(0, '/workspace/projects/src')

from tools.roster_tool import (
    add_roster_entry,
    get_roster_entries,
    get_roster_entry_by_id,
    update_roster_entry,
    delete_roster_entry,
    search_roster_entries,
    add_user_bazi
)


def test_roster():
    """测试花名册功能"""
    user_id = "test-user-123"

    print("\n" + "="*60)
    print("🧪 开始测试花名册功能")
    print("="*60 + "\n")

    # 1. 添加本人信息
    print("📝 测试1：添加本人信息")
    result1 = add_roster_entry(
        user_id=user_id,
        name="张三",
        gender="男",
        relationship_type="本人",
        birth_date="1990年03月15日08时",
        current_location="北京",
        mbti="INTJ",
        birth_place="上海",
        notes="互联网行业产品经理"
    )
    print(result1)
    print("\n")

    # 2. 添加同事信息
    print("📝 测试2：添加同事信息")
    result2 = add_roster_entry(
        user_id=user_id,
        name="李四",
        gender="女",
        relationship_type="同事",
        relationship_level="+1",
        current_location="上海",
        mbti="ENFP",
        notes="部门经理，性格开朗"
    )
    print(result2)
    print("\n")

    # 3. 获取花名册列表
    print("📋 测试3：获取花名册列表")
    result3 = get_roster_entries(user_id=user_id)
    print(result3)
    print("\n")

    # 4. 按关系类型筛选
    print("📋 测试4：按关系类型筛选（同事）")
    result4 = get_roster_entries(user_id=user_id, relationship_type="同事")
    print(result4)
    print("\n")

    # 5. 搜索花名册
    print("🔍 测试5：搜索花名册（关键词：产品经理）")
    result5 = search_roster_entries(user_id=user_id, keyword="产品经理")
    print(result5)
    print("\n")

    # 6. 获取条目详情
    print("📋 测试6：获取条目详情（假设ID为1）")
    result6 = get_roster_entry_by_id(entry_id=1)
    print(result6)
    print("\n")

    # 7. 更新条目
    print("✏️ 测试7：更新条目（假设ID为1，更新备注）")
    result7 = update_roster_entry(
        entry_id=1,
        notes="互联网高级产品经理，负责AI产品"
    )
    print(result7)
    print("\n")

    # 8. 添加八字信息
    print("🔮 测试8：为用户添加八字信息")
    result8 = add_user_bazi(
        user_id=user_id,
        bazi="庚午年己卯月乙酉日辛巳时"
    )
    print(result8)
    print("\n")

    # 9. 再次查看花名册，确认八字已更新
    print("📋 测试9：查看更新后的花名册")
    result9 = get_roster_entries(user_id=user_id)
    print(result9)
    print("\n")

    # 10. 删除条目
    print("🗑️ 测试10：删除条目（假设ID为2）")
    result10 = delete_roster_entry(entry_id=2)
    print(result10)
    print("\n")

    print("\n" + "="*60)
    print("✅ 花名册功能测试完成")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_roster()
