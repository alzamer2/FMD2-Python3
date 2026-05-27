"""
FMD2 Python - Download Manager
Multi-threaded download worker for manga chapters
"""

import os
import time
import threading
import queue
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum


class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadTask:
    """Represents a single download task"""
    id: int
    site_id: str
    manga_url: str
    manga_title: str
    chapter_url: str
    chapter_name: str
    save_path: Path
    total_pages: int = 0
    priority: int = 0
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    speed: float = 0.0
    retry_count: int = 0
    error_message: str = None


class DownloadWorker(threading.Thread):
    """Worker thread for processing download tasks"""
    
    def __init__(self, task_queue: queue.Queue, http_client, lua_handler,
                 db_manager, on_progress: Callable = None, on_complete: Callable = None):
        super().__init__(daemon=True)
        self.task_queue = task_queue
        self.http_client = http_client
        self.lua_handler = lua_handler
        self.db_manager = db_manager
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.running = True
        self.current_task = None
    
    def run(self):
        """Main worker loop"""
        while self.running:
            try:
                # Get task from queue with timeout
                try:
                    task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                if task is None:
                    # Poison pill - shutdown signal
                    break
                
                self.current_task = task
                self.process_task(task)
                self.task_queue.task_done()
                self.current_task = None
                
            except Exception as e:
                print(f"Worker error: {e}")
    
    def process_task(self, task: DownloadTask):
        """Process a single download task"""
        try:
            task.status = DownloadStatus.DOWNLOADING
            self.update_status(task)
            
            start_time = time.time()
            downloaded = 0
            
            # Get page URLs using Lua module
            page_urls = self.get_page_urls(task)
            
            if not page_urls:
                raise Exception("No pages found")
            
            task.total_pages = len(page_urls)
            
            # Download each page
            for i, page_url in enumerate(page_urls):
                if not self.running or task.status == DownloadStatus.PAUSED:
                    # Wait for resume or stop
                    while self.running and task.status == DownloadStatus.PAUSED:
                        time.sleep(0.5)
                    
                    if not self.running:
                        task.status = DownloadStatus.CANCELLED
                        break
                
                # Download image
                image_data = self.download_image(page_url)
                
                # Save image
                image_filename = f"{i+1:03d}.jpg"
                image_path = task.save_path / image_filename
                self.save_image(image_data, image_path)
                
                downloaded += 1
                
                # Update progress
                elapsed = time.time() - start_time
                task.progress = (downloaded / task.total_pages) * 100
                task.speed = downloaded / elapsed if elapsed > 0 else 0
                
                self.update_progress(task)
            
            # Create archive if needed
            if task.status != DownloadStatus.CANCELLED:
                task.status = DownloadStatus.COMPLETED
                self.create_archive(task)
                self.update_status(task)
                
                if self.on_complete:
                    self.on_complete(task)
                    
        except Exception as e:
            task.error_message = str(e)
            task.status = DownloadStatus.FAILED
            self.update_status(task)
            print(f"Download failed: {task.chapter_name} - {e}")
    
    def get_page_urls(self, task: DownloadTask) -> List[str]:
        """Get chapter page URLs using Lua module"""
        # Load module
        module = self.lua_handler.load_module(task.site_id)
        
        # Call module's chapter extraction function
        # This needs to be adapted based on FMD2 module interface
        lua_globals = self.lua_handler.get_globals()
        
        # TODO: Implement proper Lua module interface call
        # For now, return empty list
        return []
    
    def download_image(self, url: str) -> bytes:
        """Download image from URL"""
        response = self.http_client.get(url)
        response.raise_for_status()
        return response.content
    
    def save_image(self, image_data: bytes, filepath: Path):
        """Save image to file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(image_data)
    
    def create_archive(self, task: DownloadTask):
        """Create CBZ/ZIP archive from downloaded images"""
        import zipfile
        
        archive_path = task.save_path.parent / f"{task.save_path.name}.cbz"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for image_file in sorted(task.save_path.glob('*.*')):
                if image_file.is_file():
                    arcname = image_file.name
                    zipf.write(image_file, arcname)
        
        # Remove directory after creating archive
        # shutil.rmtree(task.save_path)
    
    def update_progress(self, task: DownloadTask):
        """Update task progress in database and notify callback"""
        self.db_manager.update_download_progress(
            task.id, 
            int(task.progress * task.total_pages / 100),
            task.total_pages,
            task.speed
        )
        
        if self.on_progress:
            self.on_progress(task)
    
    def update_status(self, task: DownloadTask):
        """Update task status in database"""
        self.db_manager.set_download_status(task.id, task.status.value, task.error_message)
    
    def stop(self):
        """Stop the worker"""
        self.running = False


class DownloadManager:
    """
    Manages multiple download workers and task queue
    """
    
    def __init__(self, http_client, lua_handler, db_manager, 
                 download_dir: Path, max_workers: int = 3):
        self.http_client = http_client
        self.lua_handler = lua_handler
        self.db_manager = db_manager
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_workers = max_workers
        self.task_queue = queue.Queue()
        self.workers: List[DownloadWorker] = []
        self.tasks: Dict[int, DownloadTask] = {}
        self.running = False
        
        # Progress callbacks
        self.on_task_progress: Optional[Callable] = None
        self.on_task_complete: Optional[Callable] = None
    
    def start(self):
        """Start download workers"""
        self.running = True
        
        for i in range(self.max_workers):
            worker = DownloadWorker(
                self.task_queue,
                self.http_client,
                self.lua_handler,
                self.db_manager,
                on_progress=self._on_worker_progress,
                on_complete=self._on_worker_complete
            )
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop all workers"""
        self.running = False
        
        # Send poison pills
        for _ in self.workers:
            self.task_queue.put(None)
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        self.workers.clear()
    
    def add_manga(self, url: str, module) -> bool:
        """Add manga to download queue"""
        # Get chapter list from module
        # TODO: Implement chapter listing
        
        return True
    
    def add_chapter(self, site_id: str, manga_url: str, manga_title: str,
                    chapter_url: str, chapter_name: str, priority: int = 0) -> int:
        """Add a chapter to download queue"""
        # Create save path
        safe_title = "".join(c for c in manga_title if c.isalnum() or c in ' -_')
        safe_chapter = "".join(c for c in chapter_name if c.isalnum() or c in ' -_')
        save_path = self.download_dir / safe_title / safe_chapter
        
        # Add to database
        download_id = self.db_manager.add_download(
            site_id=site_id,
            site_name="",
            manga_url=manga_url,
            manga_title=manga_title,
            chapter_name=chapter_name,
            chapter_url=chapter_url,
            save_path=str(save_path),
            priority=priority
        )
        
        if download_id > 0:
            # Create task
            task = DownloadTask(
                id=download_id,
                site_id=site_id,
                manga_url=manga_url,
                manga_title=manga_title,
                chapter_url=chapter_url,
                chapter_name=chapter_name,
                save_path=save_path,
                priority=priority
            )
            
            self.tasks[download_id] = task
            self.task_queue.put(task)
        
        return download_id
    
    def pause_download(self, download_id: int):
        """Pause a download"""
        if download_id in self.tasks:
            self.tasks[download_id].status = DownloadStatus.PAUSED
    
    def resume_download(self, download_id: int):
        """Resume a paused download"""
        if download_id in self.tasks:
            self.tasks[download_id].status = DownloadStatus.DOWNLOADING
    
    def cancel_download(self, download_id: int):
        """Cancel a download"""
        if download_id in self.tasks:
            self.tasks[download_id].status = DownloadStatus.CANCELLED
    
    def get_active_downloads(self) -> List[DownloadTask]:
        """Get all active downloads"""
        return [t for t in self.tasks.values() 
                if t.status in (DownloadStatus.DOWNLOADING, DownloadStatus.PENDING)]
    
    def _on_worker_progress(self, task: DownloadTask):
        """Handle progress update from worker"""
        if self.on_task_progress:
            self.on_task_progress(task)
    
    def _on_worker_complete(self, task: DownloadTask):
        """Handle task completion from worker"""
        if self.on_task_complete:
            self.on_task_complete(task)
