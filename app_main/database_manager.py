"""
FMD2 Python - Database Manager
SQLite database layer for favorites, downloads, and history
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class DatabaseManager:
    """
    SQLite database manager for FMD2
    Manages favorites, downloads, and reading history
    """
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connection pool
        self._local = threading.local()
        
        # Initialize database
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        return self._local.connection
    
    def _init_database(self):
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create favorites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id TEXT NOT NULL,
                site_name TEXT NOT NULL,
                manga_url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                author TEXT,
                genres TEXT,
                cover_url TEXT,
                last_chapter TEXT,
                last_chapter_url TEXT,
                last_check_time TIMESTAMP,
                new_chapters_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'ongoing',
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                enabled BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create downloads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id TEXT NOT NULL,
                site_name TEXT NOT NULL,
                manga_url TEXT NOT NULL,
                manga_title TEXT NOT NULL,
                chapter_name TEXT NOT NULL,
                chapter_url TEXT NOT NULL,
                save_path TEXT,
                total_pages INTEGER,
                downloaded_pages INTEGER DEFAULT 0,
                progress REAL DEFAULT 0.0,
                speed REAL DEFAULT 0.0,
                status TEXT DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                error_message TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_date TIMESTAMP,
                completed_date TIMESTAMP,
                file_format TEXT DEFAULT 'cbz',
                priority INTEGER DEFAULT 0
            )
        ''')
        
        # Create history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id TEXT NOT NULL,
                manga_url TEXT NOT NULL,
                manga_title TEXT NOT NULL,
                chapter_name TEXT NOT NULL,
                chapter_url TEXT NOT NULL,
                page_number INTEGER DEFAULT 1,
                read_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                device_type TEXT
            )
        ''')
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorites_site ON favorites(site_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorites_enabled ON favorites(enabled)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_downloads_status ON downloads(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_manga ON history(manga_url)')
        
        conn.commit()
    
    # Favorites operations
    
    def add_favorite(self, site_id: str, site_name: str, manga_url: str, 
                     title: str, author: str = None, genres: str = None,
                     cover_url: str = None) -> int:
        """Add a manga to favorites"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO favorites 
                (site_id, site_name, manga_url, title, author, genres, cover_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (site_id, site_name, manga_url, title, author, genres, cover_url))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding favorite: {e}")
            conn.rollback()
            return -1
    
    def remove_favorite(self, manga_url: str) -> bool:
        """Remove a manga from favorites"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM favorites WHERE manga_url = ?', (manga_url,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error removing favorite: {e}")
            conn.rollback()
            return False
    
    def get_favorites(self, enabled_only: bool = False) -> List[Dict]:
        """Get all favorites"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM favorites'
        if enabled_only:
            query += ' WHERE enabled = 1'
        query += ' ORDER BY title'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def update_favorite_last_chapter(self, manga_url: str, last_chapter: str,
                                      last_chapter_url: str = None) -> bool:
        """Update last chapter for a favorite"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE favorites 
                SET last_chapter = ?, last_chapter_url = ?, last_check_time = CURRENT_TIMESTAMP
                WHERE manga_url = ?
            ''', (last_chapter, last_chapter_url, manga_url))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating favorite: {e}")
            conn.rollback()
            return False
    
    def set_favorite_enabled(self, manga_url: str, enabled: bool) -> bool:
        """Enable or disable a favorite"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE favorites SET enabled = ? WHERE manga_url = ?
            ''', (1 if enabled else 0, manga_url))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting favorite enabled: {e}")
            conn.rollback()
            return False
    
    # Downloads operations
    
    def add_download(self, site_id: str, site_name: str, manga_url: str,
                     manga_title: str, chapter_name: str, chapter_url: str,
                     save_path: str = None, total_pages: int = 0,
                     priority: int = 0) -> int:
        """Add a chapter to download queue"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO downloads 
                (site_id, site_name, manga_url, manga_title, chapter_name, 
                 chapter_url, save_path, total_pages, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (site_id, site_name, manga_url, manga_title, chapter_name,
                  chapter_url, save_path, total_pages, priority))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding download: {e}")
            conn.rollback()
            return -1
    
    def get_downloads(self, status: str = None) -> List[Dict]:
        """Get downloads, optionally filtered by status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM downloads'
        if status:
            query += ' WHERE status = ?'
        query += ' ORDER BY priority DESC, created_date'
        
        if status:
            cursor.execute(query, (status,))
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_download_progress(self, download_id: int, downloaded_pages: int,
                                  total_pages: int = None, speed: float = 0.0) -> bool:
        """Update download progress"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if total_pages is None:
                cursor.execute('''
                    UPDATE downloads 
                    SET downloaded_pages = ?, speed = ?
                    WHERE id = ?
                ''', (downloaded_pages, speed, download_id))
            else:
                progress = (downloaded_pages / total_pages * 100) if total_pages > 0 else 0
                cursor.execute('''
                    UPDATE downloads 
                    SET downloaded_pages = ?, total_pages = ?, progress = ?, speed = ?
                    WHERE id = ?
                ''', (downloaded_pages, total_pages, progress, speed, download_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating download progress: {e}")
            conn.rollback()
            return False
    
    def set_download_status(self, download_id: int, status: str, 
                            error_message: str = None) -> bool:
        """Set download status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            updates = ['status = ?']
            params = [status]
            
            if status == 'started':
                updates.append('started_date = CURRENT_TIMESTAMP')
            elif status == 'completed':
                updates.append('completed_date = CURRENT_TIMESTAMP')
            
            if error_message:
                updates.append('error_message = ?')
                params.append(error_message)
            
            params.append(download_id)
            
            cursor.execute(f'''
                UPDATE downloads SET {', '.join(updates)} WHERE id = ?
            ''', params)
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting download status: {e}")
            conn.rollback()
            return False
    
    def increment_retry_count(self, download_id: int) -> int:
        """Increment retry count and return new count"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE downloads 
                SET retry_count = retry_count + 1 
                WHERE id = ?
                RETURNING retry_count
            ''', (download_id,))
            
            row = cursor.fetchone()
            conn.commit()
            return row[0] if row else 0
        except Exception as e:
            print(f"Error incrementing retry count: {e}")
            conn.rollback()
            return 0
    
    def delete_download(self, download_id: int) -> bool:
        """Delete a download entry"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM downloads WHERE id = ?', (download_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting download: {e}")
            conn.rollback()
            return False
    
    # History operations
    
    def add_history(self, site_id: str, manga_url: str, manga_title: str,
                    chapter_name: str, chapter_url: str, page_number: int = 1) -> int:
        """Add reading history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO history 
                (site_id, manga_url, manga_title, chapter_name, chapter_url, page_number)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (site_id, manga_url, manga_title, chapter_name, chapter_url, page_number))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding history: {e}")
            conn.rollback()
            return -1
    
    def get_history(self, manga_url: str = None, limit: int = 50) -> List[Dict]:
        """Get reading history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM history'
        if manga_url:
            query += ' WHERE manga_url = ?'
        query += ' ORDER BY read_date DESC LIMIT ?'
        
        if manga_url:
            cursor.execute(query, (manga_url, limit))
        else:
            cursor.execute(query, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # Settings operations
    
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get a setting value"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        return row[0] if row else default
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_date)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting setting: {e}")
            conn.rollback()
            return False
    
    # Statistics
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Favorites count
        cursor.execute('SELECT COUNT(*) FROM favorites')
        stats['total_favorites'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM favorites WHERE enabled = 1')
        stats['enabled_favorites'] = cursor.fetchone()[0]
        
        # Downloads count by status
        cursor.execute('''
            SELECT status, COUNT(*) FROM downloads GROUP BY status
        ''')
        stats['downloads_by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # History count
        cursor.execute('SELECT COUNT(*) FROM history')
        stats['history_entries'] = cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
