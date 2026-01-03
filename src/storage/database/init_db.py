"""
数据库初始化脚本
创建所有数据表，并初始化默认数据
"""
import logging
import hashlib
from datetime import datetime
from storage.database.shared.model import (
    Base, UserProfile, UserConversationMemory, DailyReport,
    UserAccount, UserDailyUsage, GlobalDailyUsage
)
from storage.database.db import get_engine, get_session

logger = logging.getLogger(__name__)

# 默认消耗限制配置
DEFAULT_CONFIG = {
    "global_daily_limit": 1000,  # 全局每日消耗限制
    "user_daily_limit": 300,     # 单用户每日消耗限制
}


def init_database():
    """初始化数据库，创建所有表"""
    try:
        engine = get_engine()
        # 创建所有表（如果已存在则跳过）
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("✅ 数据库表创建成功")
        logger.info("已创建的表：")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  - {table_name}")
        return True
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


def init_default_data():
    """初始化默认数据：管理员账户和默认邀请码"""
    try:
        with get_session() as session:
            # 1. 创建默认管理员账户（admin/admin）
            admin_exists = session.query(UserAccount).filter_by(username="admin").first()
            if not admin_exists:
                # 密码哈希（实际应用中应使用更安全的哈希算法如bcrypt）
                password_hash = hashlib.sha256("admin".encode()).hexdigest()

                admin = UserAccount(
                    user_id="admin",
                    username="admin",
                    password_hash=password_hash,
                    is_admin=True,
                    created_at=datetime.utcnow()
                )
                session.add(admin)
                logger.info("✅ 默认管理员账户创建成功（admin/admin）")
            else:
                logger.info("⚠️ 管理员账户已存在，跳过创建")

            # 2. 初始化全局每日消耗记录（今天）
            from datetime import date
            today = date.today().strftime("%Y-%m-%d")
            global_usage_exists = session.query(GlobalDailyUsage).filter_by(date=today).first()
            if not global_usage_exists:
                global_usage = GlobalDailyUsage(
                    date=today,
                    total_usage=0,
                    updated_at=datetime.utcnow()
                )
                session.add(global_usage)
                logger.info(f"✅ 全局消耗记录初始化成功（{today}）")

            session.commit()
            logger.info("✅ 默认数据初始化完成")

            # 显示消耗限制配置
            logger.info("=" * 50)
            logger.info("消耗限制配置：")
            logger.info(f"  全局每日限制: {DEFAULT_CONFIG['global_daily_limit']}")
            logger.info(f"  单用户每日限制: {DEFAULT_CONFIG['user_daily_limit']}")
            logger.info("=" * 50)

            return True
    except Exception as e:
        logger.error(f"❌ 默认数据初始化失败: {e}")
        session.rollback()
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("=" * 50)
    logger.info("开始初始化数据库...")
    logger.info("=" * 50)
    init_database()
    init_default_data()
    logger.info("=" * 50)
    logger.info("数据库初始化完成！")
    logger.info("=" * 50)
