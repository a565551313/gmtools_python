"""
活动管理系统数据库模型
支持大转盘、抽奖券等多种活动类型
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from services.gift_service import GiftService

logger = logging.getLogger(__name__)

# 导入数据库连接
try:
    from database.connection import db
    def get_db_connection():
        return db.get_connection()
except ImportError:
    def get_db_connection():
        import os
        from sqlite3 import connect
        DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gmtools.db")
        conn = connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

@dataclass
class Activity:
    """活动基础模型"""
    id: Optional[int] = None
    name: str = ""
    type: str = ""  # roulette, lottery, scratch等
    description: str = ""
    game_id_required: bool = True  # 是否需要游戏ID
    max_participations: int = 0  # 最大参与次数，0表示无限制
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_active: bool = True
    config: str = ""  # JSON配置
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class ActivityReward:
    """活动奖项模型"""
    id: Optional[int] = None
    activity_id: int = 0
    name: str = ""  # 奖项名称
    description: str = ""  # 奖项描述
    type: str = "item"  # item, currency, equipment等
    value: str = ""  # 奖励值(JSON)
    probability: float = 0.0  # 中奖率(0-100)
    total_quantity: int = 0  # 总数量
    remaining_quantity: int = 0  # 剩余数量
    icon: str = ""  # 图标
    order_index: int = 0  # 显示顺序
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class ActivityParticipation:
    """活动参与记录"""
    id: Optional[int] = None
    activity_id: int = 0
    game_id: str = ""
    reward_id: Optional[int] = None  # 中奖的奖项ID
    reward_name: str = ""  # 中奖名称
    status: int = 1  # 1: 成功, 2: 失败/待补发
    ip_address: str = ""
    user_agent: str = ""
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

class ActivityManager:
    """活动管理器"""
    
    def __init__(self):
        self.gift_service = None
        self.init_tables()
        
    def set_gift_service(self, service):
        """设置礼包服务"""
        self.gift_service = service
    
    def init_tables(self):
        """初始化数据表"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 活动表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT DEFAULT '',
            game_id_required INTEGER DEFAULT 1,
            max_participations INTEGER DEFAULT 0,
            start_time DATETIME,
            end_time DATETIME,
            is_active INTEGER DEFAULT 1,
            config TEXT DEFAULT '{}',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 活动奖项表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            type TEXT DEFAULT 'item',
            value TEXT DEFAULT '{}',
            probability REAL DEFAULT 0.0,
            total_quantity INTEGER DEFAULT 0,
            remaining_quantity INTEGER DEFAULT 0,
            icon TEXT DEFAULT '',
            order_index INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (activity_id) REFERENCES activities (id) ON DELETE CASCADE
        )
        ''')
        
        # 活动参与记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_participations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            game_id TEXT NOT NULL,
            reward_id INTEGER,
            reward_name TEXT DEFAULT '',
            status INTEGER DEFAULT 1,
            ip_address TEXT,
            user_agent TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (activity_id) REFERENCES activities (id) ON DELETE CASCADE,
            FOREIGN KEY (reward_id) REFERENCES activity_rewards (id) ON DELETE SET NULL
        )
        ''')
        
        # 检查是否需要添加 status 字段 (针对已有表)
        try:
            cursor.execute('SELECT status FROM activity_participations LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE activity_participations ADD COLUMN status INTEGER DEFAULT 1')
        
        # 索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_active ON activities(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_rewards_activity ON activity_rewards(activity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_participations_activity ON activity_participations(activity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_participations_game_id ON activity_participations(game_id)')
        
        conn.commit()
        conn.close()
    
    def create_activity(self, activity: Activity) -> int:
        """创建活动"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO activities (name, type, description, game_id_required, max_participations, 
                               start_time, end_time, config)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (activity.name, activity.type, activity.description, activity.game_id_required,
              activity.max_participations, activity.start_time, activity.end_time, activity.config))
        
        activity_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return activity_id
    
    def update_activity(self, activity_id: int, activity: Activity) -> bool:
        """更新活动"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE activities SET name=?, type=?, description=?, game_id_required=?, max_participations=?,
                             start_time=?, end_time=?, config=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
        ''', (activity.name, activity.type, activity.description, activity.game_id_required,
              activity.max_participations, activity.start_time, activity.end_time, 
              activity.config, activity_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_activity(self, activity_id: int) -> Optional[Activity]:
        """获取活动信息"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM activities WHERE id=?', (activity_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # 转换 game_id_required 和 is_active 为布尔值
            row_dict = dict(row)
            row_dict['game_id_required'] = bool(row_dict['game_id_required'])
            row_dict['is_active'] = bool(row_dict['is_active'])
            return Activity(**row_dict)
        return None
    
    def get_activities(self, limit: int = 100, offset: int = 0) -> List[Activity]:
        """获取活动列表"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM activities ORDER BY created_at DESC LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        activities = []
        for row in rows:
            # 转换 game_id_required 和 is_active 为布尔值
            row_dict = dict(row)
            row_dict['game_id_required'] = bool(row_dict['game_id_required'])
            row_dict['is_active'] = bool(row_dict['is_active'])
            activities.append(Activity(**row_dict))
        
        return activities
    
    def add_reward(self, reward: ActivityReward) -> int:
        """添加奖项"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO activity_rewards (activity_id, name, description, type, value, 
                                     probability, total_quantity, remaining_quantity, icon, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reward.activity_id, reward.name, reward.description, reward.type,
              reward.value, reward.probability, reward.total_quantity,
              reward.remaining_quantity, reward.icon, reward.order_index))
        
        reward_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reward_id
    
    def get_rewards(self, activity_id: int) -> List[ActivityReward]:
        """获取活动奖项"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM activity_rewards WHERE activity_id=? ORDER BY order_index ASC
        ''', (activity_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ActivityReward(**row) for row in rows]
    
    def participate(self, activity_id: int, game_id: str, ip_address: str = "", 
                   user_agent: str = "") -> Dict[str, Any]:
        """参与活动"""
        import random
        
        try:
            activity = self.get_activity(activity_id)
            if not activity or not activity.is_active:
                return {"success": False, "message": "活动不存在或未激活"}
            
            # 检查时间（简化版，避免时区问题）
            now = datetime.now()
            
            if activity.start_time:
                try:
                    # 简化时间比较，只比较字符串
                    if str(now) < activity.start_time:
                        return {"success": False, "message": "活动尚未开始"}
                except Exception as e:
                    logger.error(f"时间比较失败: {str(e)}")
                    # 忽略时间比较错误，继续执行

            if activity.end_time:
                try:
                    # 简化时间比较，只比较字符串
                    if str(now) > activity.end_time:
                        return {"success": False, "message": "活动已结束"}
                except Exception as e:
                    logger.error(f"时间比较失败: {str(e)}")
                    # 忽略时间比较错误，继续执行
            
            # 检查参与次数限制
            if activity.max_participations > 0:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT COUNT(*) as count FROM activity_participations 
                WHERE activity_id=? AND game_id=?
                ''', (activity_id, game_id))
                
                participated_count = cursor.fetchone()['count']
                conn.close()
                
                if participated_count >= activity.max_participations:
                    return {"success": False, "message": f"已达到最大参与次数({activity.max_participations})"}
            
            # 获取奖项
            rewards = self.get_rewards(activity_id)
            # 只有剩余数量>0的奖项才参与抽奖
            available_rewards = [r for r in rewards if r.remaining_quantity > 0]

            logger.info(f"活动 {activity_id} 的可用奖项: {len(available_rewards)}个，总概率: {sum(r.probability for r in available_rewards)}%")

            # 如果没有可用奖项，记录警告
            if not available_rewards:
                logger.warning(f"活动 {activity_id} 没有可用奖项（所有奖品剩余数量为0）")
            
            # 随机抽奖
            total_probability = sum(r.probability for r in available_rewards)

            # 加权随机选择 (基于100%)
            rand_val = random.uniform(0, 100)
            cumulative = 0
            selected_reward = None

            # 只有当随机数在总概率范围内时才可能中奖
            if rand_val <= total_probability:
                for reward in available_rewards:
                    cumulative += reward.probability
                    if rand_val <= cumulative:
                        selected_reward = reward
                        break
            
            # 记录参与
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 尝试发放奖励
            status = 1 # 1: 成功, 2: 失败/待补发
            reward_message = selected_reward.name if selected_reward else "谢谢参与"

            if selected_reward:
                try:
                    # 检查奖品是否可以发放
                    if selected_reward.remaining_quantity > 0:
                        # 有剩余数量，尝试发放
                        success = self.distribute_reward(game_id, selected_reward)
                        status = 1 if success else 2
                        logger.info(f"发放奖品 {selected_reward.name}: success={success}")
                    elif selected_reward.remaining_quantity == -1:
                        # 特殊奖项（无限数量），直接标记为成功
                        status = 1
                        logger.info(f"特殊奖项 {selected_reward.name} 中奖")
                    else:
                        # 奖品已无剩余，但仍按概率中奖，当作谢谢参与
                        status = 1
                        reward_message = "谢谢参与"
                        logger.info(f"奖品 {selected_reward.name} 已无剩余，当作谢谢参与")
                except Exception as e:
                    logger.error(f"自动发奖失败: {str(e)}")
                    status = 2
            
            participation = ActivityParticipation(
                activity_id=activity_id,
                game_id=game_id,
                reward_id=selected_reward.id if selected_reward else None,
                reward_name=reward_message,
                status=status,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            cursor.execute('''
            INSERT INTO activity_participations (activity_id, game_id, reward_id, reward_name, status, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (participation.activity_id, participation.game_id, participation.reward_id,
                  participation.reward_name, participation.status, participation.ip_address, participation.user_agent))
            
            # 减少剩余数量（只对有剩余数量的奖项）
            if selected_reward and selected_reward.remaining_quantity > 0:
                cursor.execute('''
                UPDATE activity_rewards SET remaining_quantity = remaining_quantity - 1 
                WHERE id=?
                ''', (selected_reward.id,))
            
            conn.commit()
            conn.close()
            
            # 根据实际发放结果返回消息
            if selected_reward:
                if reward_message == "谢谢参与":
                    message = "谢谢参与，下次再来！"
                else:
                    message = f"恭喜获得：{reward_message}"
            else:
                message = "谢谢参与，下次再来！"

            return {
                "success": True,
                "message": message,
                "reward": selected_reward.to_dict() if selected_reward else None
            }
        except Exception as e:
            logger.error(f"参与活动失败: {str(e)}")
            # 返回友好的错误信息，而不是抛出500错误
            return {
                "success": False,
                "message": f"参与失败: {str(e)}",
                "reward": None
            }
    
    def get_participations(
        self, 
        activity_id: int, 
        limit: int = 100, 
        offset: int = 0,
        game_id: Optional[str] = None,
        reward_name: Optional[str] = None,
        status: Optional[int] = None,
        activity_type: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取参与记录（带筛选）"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = ["p.activity_id=?"]
        params = [activity_id]
        
        if game_id:
            conditions.append("p.game_id LIKE ?")
            params.append(f"%{game_id}%")
            
        if reward_name:
            conditions.append("p.reward_name LIKE ?")
            params.append(f"%{reward_name}%")
            
        if status:
            conditions.append("p.status=?")
            params.append(status)
            
        if activity_type:
            conditions.append("a.type=?")
            params.append(activity_type)
            
        where_clause = " AND ".join(conditions)
        
        # 查询总数
        count_sql = f'''
        SELECT COUNT(*) 
        FROM activity_participations p
        JOIN activities a ON p.activity_id = a.id
        WHERE {where_clause}
        '''
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]
        
        # 查询记录
        sql = f'''
        SELECT p.*, a.type as activity_type
        FROM activity_participations p
        JOIN activities a ON p.activity_id = a.id
        WHERE {where_clause}
        ORDER BY p.created_at DESC 
        LIMIT ? OFFSET ?
        '''
        
        cursor.execute(sql, params + [limit, offset])
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            item = dict(row)
            result.append(item)
            
        return result, total

    def get_user_participations(self, activity_id: int, game_id: str) -> List[ActivityParticipation]:
        """获取指定用户的参与记录"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM activity_participations 
        WHERE activity_id=? AND game_id=?
        ORDER BY created_at DESC
        ''', (activity_id, game_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ActivityParticipation(**row) for row in rows]
    
    def distribute_reward(self, game_id: str, reward: Any) -> bool:
        """发放奖励"""
        if not reward.value:
            return True
            
        try:
            reward_config = json.loads(reward.value)
            
            if not self.gift_service:
                logger.error("GiftService未初始化，无法自动发奖")
                return False
            
            # 根据配置发放奖励
            # 格式示例: {"item_name": "屠龙刀", "quantity": 1, "category": "default"}
            # 或者: {"gem_name": "红宝石", "min_level": 1, "max_level": 1}
            
            if "item_name" in reward_config:
                return self.gift_service.give_item(
                    game_id, 
                    reward_config["item_name"], 
                    reward_config.get("quantity", 1),
                    reward_config.get("category", "default")
                )
            elif "gem_name" in reward_config:
                return self.gift_service.give_gem(
                    game_id,
                    reward_config["gem_name"],
                    reward_config.get("min_level", 1),
                    reward_config.get("max_level", 1)
                )
            else:
                logger.warning(f"未知的奖励配置格式: {reward.value}")
                return False
                
        except Exception as e:
            logger.error(f"发放奖励异常: {str(e)}")
            return False

    def resend_reward(self, participation_id: int) -> Tuple[bool, str]:
        """补发奖励"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            logger.info(f"查询参与记录: {participation_id}")

            # 获取记录
            cursor.execute('''
            SELECT p.*, r.value as reward_value
            FROM activity_participations p
            LEFT JOIN activity_rewards r ON p.reward_id = r.id
            WHERE p.id=?
            ''', (participation_id,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                logger.warning(f"参与记录不存在: {participation_id}")
                return False, "记录不存在"

            logger.info(f"找到记录: game_id={row['game_id']}, reward_id={row['reward_id']}, status={row['status']}")

            if not row['reward_id']:
                logger.warning(f"记录没有奖品: {participation_id}")
                return False, "该记录没有奖品"

            # 构造临时 reward 对象用于发放
            @dataclass
            class TempReward:
                value: str

            reward = TempReward(value=row['reward_value'])
            logger.info(f"准备发放奖励: game_id={row['game_id']}, reward_value={row['reward_value']}")

            success = self.distribute_reward(row['game_id'], reward)

            # 更新状态
            new_status = 1 if success else 2
            status_updated = self.update_participation_status(participation_id, new_status)

            logger.info(f"补发完成: success={success}, status_updated={status_updated}")

            return success, "补发成功" if success else "补发失败"

        except Exception as e:
            logger.error(f"补发奖励异常: {str(e)}", exc_info=True)
            # 即使出错也要尝试更新状态
            try:
                self.update_participation_status(participation_id, 2)
            except Exception as status_error:
                logger.error(f"更新状态也失败: {str(status_error)}")
            return False, f"补发异常: {str(e)}"

    def update_participation_status(self, participation_id: int, status: int) -> bool:
        """更新参与记录状态"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE activity_participations SET status=? WHERE id=?', (status, participation_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def delete_activity(self, activity_id: int) -> bool:
        """删除活动"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM activities WHERE id=?', (activity_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_reward(self, reward_id: int) -> bool:
        """删除奖项"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM activity_rewards WHERE id=?', (reward_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def update_reward(self, reward_id: int, reward: ActivityReward) -> bool:
        """更新奖项"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE activity_rewards
            SET name=?, description=?, type=?, value=?, probability=?,
                total_quantity=?, remaining_quantity=?, icon=?, order_index=?
            WHERE id=?
            ''', (
                reward.name, reward.description, reward.type, reward.value,
                reward.probability, reward.total_quantity, reward.remaining_quantity,
                reward.icon, reward.order_index, reward_id
            ))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating reward: {e}")
            return False
        finally:
            conn.close()
    
    def get_statistics(self, activity_id: int) -> Dict[str, Any]:
        """获取活动统计"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 总参与次数
        cursor.execute('''
        SELECT COUNT(*) as total_participations FROM activity_participations WHERE activity_id=?
        ''', (activity_id,))
        total_participations = cursor.fetchone()['total_participations']
        
        # 唯一用户数
        cursor.execute('''
        SELECT COUNT(DISTINCT game_id) as unique_users FROM activity_participations WHERE activity_id=?
        ''', (activity_id,))
        unique_users = cursor.fetchone()['unique_users']
        
        # 中奖次数
        cursor.execute('''
        SELECT COUNT(*) as winning_count FROM activity_participations WHERE activity_id=? AND reward_id IS NOT NULL
        ''', (activity_id,))
        winning_count = cursor.fetchone()['winning_count']
        
        # 奖项统计
        cursor.execute('''
        SELECT ar.name, ar.total_quantity, ar.remaining_quantity, 
               COUNT(ap.id) as won_count
        FROM activity_rewards ar
        LEFT JOIN activity_participations ap ON ar.id = ap.reward_id
        WHERE ar.activity_id=?
        GROUP BY ar.id
        ORDER BY ar.order_index
        ''', (activity_id,))
        
        reward_stats = []
        for row in cursor.fetchall():
            reward_stats.append({
                "name": row['name'],
                "total_quantity": row['total_quantity'],
                "remaining_quantity": row['remaining_quantity'],
                "won_count": row['won_count'],
                "win_rate": (row['won_count'] / total_participations * 100) if total_participations > 0 else 0
            })
        
        conn.close()
        
        return {
            "total_participations": total_participations,
            "unique_users": unique_users,
            "winning_count": winning_count,
            "win_rate": (winning_count / total_participations * 100) if total_participations > 0 else 0,
            "reward_stats": reward_stats
        }
    
    def delete_participation(self, participation_id: int) -> bool:
        """删除单条参与记录"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM activity_participations WHERE id=?', (participation_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def clear_participations(self, activity_id: int) -> bool:
        """清空指定活动的所有参与记录"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM activity_participations WHERE activity_id=?', (activity_id,))
        conn.commit()
        conn.close()
        return True