"""
缓存预热模块

用于在应用启动时预加载热点数据到缓存，提升系统响应速度。
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.redis import redis_manager
from app.models.alert import AlertSetting
from app.models.emergency_contact import EmergencyContact
from app.models.user import User
from app.services.alert_service import AlertService
from app.services.emergency_contact_service import EmergencyContactService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)


class CacheWarmer:
    """缓存预热器"""

    def __init__(self):
        self.warmed_count = 0
        self.errors = []

    def warm_all(self, db: Optional[Session] = None) -> dict:
        """
        预热所有缓存

        Args:
            db: 数据库会话，如果为None则创建新会话

        Returns:
            dict: 预热结果统计
        """
        start_time = datetime.utcnow()
        self.warmed_count = 0
        self.errors = []

        # 检查Redis是否可用
        if not redis_manager.check_health():
            logger.warning("Redis不可用，跳过缓存预热")
            return {
                "success": False,
                "message": "Redis不可用",
                "warmed_count": 0,
                "duration_ms": 0,
            }

        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            # 预热活跃用户数据
            self._warm_active_users(db)

            # 预热预警配置
            self._warm_alert_settings(db)

            # 预热紧急联系人
            self._warm_emergency_contacts(db)

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            result = {
                "success": True,
                "warmed_count": self.warmed_count,
                "errors": self.errors,
                "duration_ms": round(duration, 2),
            }

            logger.info(f"缓存预热完成: 预热了 {self.warmed_count} 条数据，耗时 {duration:.2f}ms")
            return result

        except Exception as e:
            logger.error(f"缓存预热失败: {e}")
            return {
                "success": False,
                "message": str(e),
                "warmed_count": self.warmed_count,
                "errors": self.errors,
            }
        finally:
            if close_db:
                db.close()

    def _warm_active_users(self, db: Session) -> int:
        """
        预热活跃用户数据

        预热最近7天内有登录的用户数据
        """
        try:
            # 获取最近7天登录的用户
            since = datetime.utcnow() - timedelta(days=7)
            active_users = (
                db.query(User).filter(User.last_sign_in >= since).limit(100).all()
            )

            count = 0
            for user in active_users:
                try:
                    # 触发UserService的缓存机制
                    UserService.get_user_by_id(db, user.user_id)
                    count += 1
                except Exception as e:
                    self.errors.append(f"预热用户 {user.user_id} 失败: {e}")

            self.warmed_count += count
            logger.info(f"预热了 {count} 个活跃用户数据")
            return count

        except Exception as e:
            logger.error(f"预热活跃用户数据失败: {e}")
            self.errors.append(f"预热活跃用户数据失败: {e}")
            return 0

    def _warm_alert_settings(self, db: Session) -> int:
        """
        预热预警配置数据

        预热所有启用了预警的用户的配置
        """
        try:
            # 获取启用了预警的配置
            alert_settings = (
                db.query(AlertSetting)
                .filter(AlertSetting.checkin_enabled)
                .limit(100)
                .all()
            )

            count = 0
            for setting in alert_settings:
                try:
                    # 触发AlertService的缓存机制
                    AlertService.get_setting(db, setting.user_id)
                    count += 1
                except Exception as e:
                    self.errors.append(f"预热预警配置 {setting.user_id} 失败: {e}")

            self.warmed_count += count
            logger.info(f"预热了 {count} 个预警配置数据")
            return count

        except Exception as e:
            logger.error(f"预热预警配置数据失败: {e}")
            self.errors.append(f"预热预警配置数据失败: {e}")
            return 0

    def _warm_emergency_contacts(self, db: Session) -> int:
        """
        预热紧急联系人数据

        预热有紧急联系人的用户数据
        """
        try:
            # 获取有紧急联系人的用户ID列表
            user_ids = db.query(EmergencyContact.user_id).distinct().limit(100).all()
            user_ids = [uid[0] for uid in user_ids]

            count = 0
            for user_id in user_ids:
                try:
                    # 触发EmergencyContactService的缓存机制
                    EmergencyContactService().get_emergency_contacts(db, user_id)
                    count += 1
                except Exception as e:
                    self.errors.append(f"预热紧急联系人 {user_id} 失败: {e}")

            self.warmed_count += count
            logger.info(f"预热了 {count} 个用户的紧急联系人数据")
            return count

        except Exception as e:
            logger.error(f"预热紧急联系人数据失败: {e}")
            self.errors.append(f"预热紧急联系人数据失败: {e}")
            return 0


# 全局缓存预热器实例
cache_warmer = CacheWarmer()


def warm_cache_on_startup():
    """
    应用启动时调用此函数预热缓存

    可以在main.py中调用此函数
    """
    logger.info("开始缓存预热...")
    result = cache_warmer.warm_all()

    if result["success"]:
        logger.info(f"✓ 缓存预热成功: {result['warmed_count']} 条数据已预热")
    else:
        logger.warning(f"✗ 缓存预热失败: {result.get('message', '未知错误')}")

    return result
