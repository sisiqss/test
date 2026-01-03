"""
花名册功能简单测试脚本（直接操作数据库）
"""
import logging
import sys
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加src到路径
sys.path.insert(0, '/workspace/projects/src')

from storage.database.db import get_session
from storage.database.shared.model import (
    UserProfile,
    RelationshipType,
    RelationshipLevel
)


def test_roster():
    """测试花名册功能"""
    user_id = "test-user-123"

    print("\n" + "="*60)
    print("🧪 开始测试花名册功能")
    print("="*60 + "\n")

    try:
        # 1. 添加本人信息
        print("📝 测试1：添加本人信息")
        with get_session() as session:
            entry1 = UserProfile(
                user_id=user_id,
                name="张三",
                gender="男",
                relationship_type=RelationshipType.SELF,
                birth_date="1990年03月15日08时",
                current_location="北京",
                mbti="INTJ",
                birth_place="上海",
                notes="互联网行业产品经理"
            )
            session.add(entry1)
            session.commit()
            session.refresh(entry1)
            print(f"✅ 添加成功！ID: {entry1.id}, 姓名: {entry1.name}")
        print("\n")

        # 2. 添加同事信息
        print("📝 测试2：添加同事信息")
        with get_session() as session:
            entry2 = UserProfile(
                user_id=user_id,
                name="李四",
                gender="女",
                relationship_type=RelationshipType.COLLEAGUE,
                relationship_level=RelationshipLevel.LEVEL_1_SUPERIOR,
                current_location="上海",
                mbti="ENFP",
                notes="部门经理，性格开朗"
            )
            session.add(entry2)
            session.commit()
            session.refresh(entry2)
            print(f"✅ 添加成功！ID: {entry2.id}, 姓名: {entry2.name}")
        print("\n")

        # 3. 添加朋友信息
        print("📝 测试3：添加朋友信息")
        with get_session() as session:
            entry3 = UserProfile(
                user_id=user_id,
                name="王五",
                gender="男",
                relationship_type=RelationshipType.FRIEND,
                current_location="广州",
                mbti="ISTP",
                notes="大学同学，现在在创业"
            )
            session.add(entry3)
            session.commit()
            session.refresh(entry3)
            print(f"✅ 添加成功！ID: {entry3.id}, 姓名: {entry3.name}")
        print("\n")

        # 4. 获取花名册列表
        print("📋 测试4：获取花名册列表")
        with get_session() as session:
            entries = session.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).order_by(UserProfile.created_at.desc()).all()

            print(f"📋 花名册（共 {len(entries)} 条）：\n")
            for entry in entries:
                rel_type = {
                    RelationshipType.SELF: "本人",
                    RelationshipType.COLLEAGUE: "同事",
                    RelationshipType.PARENT: "父母",
                    RelationshipType.CHILD: "儿女",
                    RelationshipType.FRIEND: "朋友",
                    RelationshipType.OTHER: "其他",
                }.get(entry.relationship_type, entry.relationship_type)

                rel_level = f" ({entry.relationship_level.value})" if entry.relationship_level else ""

                print(f"**{entry.name}** - {rel_type}{rel_level}")
                print(f"  性别: {entry.gender} | 现居地: {entry.current_location}")
                if entry.birth_date:
                    print(f"  出生日期: {entry.birth_date}")
                if entry.mbti:
                    print(f"  MBTI: {entry.mbti}")
                if entry.bazi:
                    print(f"  八字: {entry.bazi}")
                if entry.birth_place:
                    print(f"  出生地: {entry.birth_place}")
                if entry.notes:
                    print(f"  备注: {entry.notes}")
                print()
        print("\n")

        # 5. 按关系类型筛选
        print("📋 测试5：按关系类型筛选（同事）")
        with get_session() as session:
            colleagues = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.relationship_type == RelationshipType.COLLEAGUE
            ).all()

            print(f"📋 同事列表（共 {len(colleagues)} 条）：\n")
            for entry in colleagues:
                print(f"**{entry.name}** - 同事 ({entry.relationship_level.value})")
                print(f"  现居地: {entry.current_location} | MBTI: {entry.mbti}")
                if entry.notes:
                    print(f"  备注: {entry.notes}")
                print()
        print("\n")

        # 6. 更新条目
        print("✏️ 测试6：更新条目（ID=1，更新备注和八字）")
        with get_session() as session:
            entry = session.query(UserProfile).filter(UserProfile.id == 1).first()
            if entry:
                entry.notes = "互联网高级产品经理，负责AI产品，已有5年经验"
                entry.bazi = "庚午年己卯月乙酉日辛巳时"
                entry.updated_at = datetime.utcnow()
                session.commit()
                print(f"✅ 更新成功！")
                print(f"  姓名: {entry.name}")
                print(f"  新备注: {entry.notes}")
                print(f"  八字: {entry.bazi}")
            else:
                print("❌ 未找到ID为1的条目")
        print("\n")

        # 7. 搜索条目
        print("🔍 测试7：搜索花名册（关键词：创业）")
        with get_session() as session:
            results = session.query(UserProfile).filter(
                UserProfile.user_id == user_id,
                UserProfile.notes.ilike("%创业%")
            ).all()

            print(f"🔍 搜索结果（共 {len(results)} 条）：\n")
            for entry in results:
                print(f"**{entry.name}** (ID: {entry.id})")
                print(f"  备注: {entry.notes}")
                print()
        print("\n")

        # 8. 删除条目
        print("🗑️ 测试8：删除条目（ID=3）")
        with get_session() as session:
            entry = session.query(UserProfile).filter(UserProfile.id == 3).first()
            if entry:
                name = entry.name
                session.delete(entry)
                session.commit()
                print(f"✅ 删除成功！已删除：{name}")
            else:
                print("❌ 未找到ID为3的条目")
        print("\n")

        # 9. 查看最终花名册
        print("📋 测试9：查看最终花名册")
        with get_session() as session:
            entries = session.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).order_by(UserProfile.created_at.desc()).all()

            print(f"📋 最终花名册（共 {len(entries)} 条）：\n")
            for entry in entries:
                rel_type = {
                    RelationshipType.SELF: "本人",
                    RelationshipType.COLLEAGUE: "同事",
                    RelationshipType.PARENT: "父母",
                    RelationshipType.CHILD: "儿女",
                    RelationshipType.FRIEND: "朋友",
                    RelationshipType.OTHER: "其他",
                }.get(entry.relationship_type, entry.relationship_type)

                rel_level = f" ({entry.relationship_level.value})" if entry.relationship_level else ""

                print(f"**{entry.name}** - {rel_type}{rel_level}")
                print(f"  性别: {entry.gender} | 现居地: {entry.current_location}")
                if entry.birth_date:
                    print(f"  出生日期: {entry.birth_date}")
                if entry.mbti:
                    print(f"  MBTI: {entry.mbti}")
                if entry.bazi:
                    print(f"  八字: {entry.bazi}")
                if entry.birth_place:
                    print(f"  出生地: {entry.birth_place}")
                if entry.notes:
                    print(f"  备注: {entry.notes}")
                print()
        print("\n")

        print("\n" + "="*60)
        print("✅ 花名册功能测试完成！所有测试通过！")
        print("="*60 + "\n")

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("❌ 花名册功能测试失败")
        print("="*60 + "\n")


if __name__ == "__main__":
    test_roster()
