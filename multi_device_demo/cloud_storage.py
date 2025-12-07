"""
Cloud Coordinator Storage Layer
Stores all tasks and results in SQLite database
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from network_config import DATABASE_PATH, RESULT_CACHE_HOURS


class CloudStorage:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with schema"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                gamer_id TEXT NOT NULL,
                peer_id TEXT,
                task_type TEXT NOT NULL,
                task_data TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at REAL NOT NULL,
                assigned_at REAL,
                completed_at REAL,
                cost_usd REAL
            )
        """)
        
        # Results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                result_data TEXT NOT NULL,
                processing_time_ms REAL,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            )
        """)
        
        # Peers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peers (
                peer_id TEXT PRIMARY KEY,
                ip_address TEXT,
                connected_at REAL NOT NULL,
                last_heartbeat REAL NOT NULL,
                total_earned_usd REAL DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Gamers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gamers (
                gamer_id TEXT PRIMARY KEY,
                ip_address TEXT,
                connected_at REAL NOT NULL,
                last_activity REAL NOT NULL,
                total_spent_usd REAL DEFAULT 0,
                tasks_submitted INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        self.conn.commit()
        print(f"💾 Database initialized: {self.db_path}")
    
    def store_task(self, task_id: str, gamer_id: str, task_type: str, 
                   task_data: Dict[str, Any]) -> bool:
        """Store a new task"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (task_id, gamer_id, task_type, task_data, 
                                 status, created_at)
                VALUES (?, ?, ?, ?, 'pending', ?)
            """, (task_id, gamer_id, task_type, json.dumps(task_data), time.time()))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error storing task: {e}")
            return False
    
    def assign_task_to_peer(self, task_id: str, peer_id: str) -> bool:
        """Mark task as assigned to a peer"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE tasks 
                SET peer_id = ?, status = 'assigned', assigned_at = ?
                WHERE task_id = ?
            """, (peer_id, time.time(), task_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error assigning task: {e}")
            return False
    
    def store_result(self, task_id: str, result_data: Dict[str, Any], 
                    processing_time_ms: float, cost_usd: float) -> bool:
        """Store task result"""
        try:
            cursor = self.conn.cursor()
            expires_at = time.time() + (RESULT_CACHE_HOURS * 3600)
            
            # Store result
            cursor.execute("""
                INSERT INTO results (task_id, result_data, processing_time_ms, 
                                   created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (task_id, json.dumps(result_data), processing_time_ms, 
                  time.time(), expires_at))
            
            # Update task status
            cursor.execute("""
                UPDATE tasks 
                SET status = 'completed', completed_at = ?, cost_usd = ?
                WHERE task_id = ?
            """, (time.time(), cost_usd, task_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error storing result: {e}")
            return False
    
    def get_cached_result(self, task_type: str, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if we have a cached result for this exact task"""
        try:
            cursor = self.conn.cursor()
            task_data_json = json.dumps(task_data, sort_keys=True)
            
            cursor.execute("""
                SELECT r.result_data, r.processing_time_ms
                FROM results r
                JOIN tasks t ON r.task_id = t.task_id
                WHERE t.task_type = ? 
                  AND t.task_data = ?
                  AND r.expires_at > ?
                  AND t.status = 'completed'
                ORDER BY r.created_at DESC
                LIMIT 1
            """, (task_type, task_data_json, time.time()))
            
            row = cursor.fetchone()
            if row:
                return {
                    "result": json.loads(row[0]),
                    "processing_time_ms": row[1],
                    "cached": True
                }
            return None
        except Exception as e:
            print(f"❌ Error checking cache: {e}")
            return None
    
    def register_peer(self, peer_id: str, ip_address: str) -> bool:
        """Register or update peer"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO peers (peer_id, ip_address, connected_at, last_heartbeat)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(peer_id) DO UPDATE SET
                    connected_at = excluded.connected_at,
                    last_heartbeat = excluded.last_heartbeat,
                    is_active = 1
            """, (peer_id, ip_address, time.time(), time.time()))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error registering peer: {e}")
            return False
    
    def update_peer_earnings(self, peer_id: str, amount: float) -> bool:
        """Update peer earnings"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE peers
                SET total_earned_usd = total_earned_usd + ?,
                    tasks_completed = tasks_completed + 1,
                    last_heartbeat = ?
                WHERE peer_id = ?
            """, (amount, time.time(), peer_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error updating peer earnings: {e}")
            return False
    
    def register_gamer(self, gamer_id: str, ip_address: str) -> bool:
        """Register or update gamer"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO gamers (gamer_id, ip_address, connected_at, last_activity)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(gamer_id) DO UPDATE SET
                    connected_at = excluded.connected_at,
                    last_activity = excluded.last_activity,
                    is_active = 1
            """, (gamer_id, ip_address, time.time(), time.time()))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error registering gamer: {e}")
            return False
    
    def update_gamer_spending(self, gamer_id: str, amount: float) -> bool:
        """Update gamer spending"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE gamers
                SET total_spent_usd = total_spent_usd + ?,
                    tasks_submitted = tasks_submitted + 1,
                    last_activity = ?
                WHERE gamer_id = ?
            """, (amount, time.time(), gamer_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error updating gamer spending: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get network statistics"""
        try:
            cursor = self.conn.cursor()
            
            # Total stats
            cursor.execute("SELECT COUNT(*), SUM(cost_usd) FROM tasks WHERE status = 'completed'")
            total_tasks, total_revenue = cursor.fetchone()
            
            # Active peers
            cursor.execute("SELECT COUNT(*) FROM peers WHERE is_active = 1")
            active_peers = cursor.fetchone()[0]
            
            # Active gamers
            cursor.execute("SELECT COUNT(*) FROM gamers WHERE is_active = 1")
            active_gamers = cursor.fetchone()[0]
            
            return {
                "total_tasks_completed": total_tasks or 0,
                "total_revenue_usd": round(total_revenue or 0, 6),
                "active_peers": active_peers,
                "active_gamers": active_gamers
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def cleanup_expired_results(self):
        """Remove expired cached results"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM results WHERE expires_at < ?", (time.time(),))
            deleted = cursor.rowcount
            self.conn.commit()
            if deleted > 0:
                print(f"🧹 Cleaned up {deleted} expired results")
        except Exception as e:
            print(f"❌ Error cleaning up: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
