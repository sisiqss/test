"""
数据库初始化脚本
创建所有数据表
"""
import logging
from storage.database.shared.model import Base, UserProfile, UserConversationMemory
from storage.database.db import get_engine

logger = logging.getLogger(__name__)


def init_database():
    """初始化数据库，创建所有表"""
    try:
        engine = get_engine()
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表创建成功")
        logger.info("已创建的表：")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  - {table_name}")
        return True
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database()
