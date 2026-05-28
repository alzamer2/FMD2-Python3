"""
FMD2 Python - Downloads View
Shows active downloads with progress bars and controls
"""

import flet as ft
from typing import List, Dict, Optional


class DownloadsView:
    """
    Downloads view showing active and completed downloads
    """
    
    def __init__(self, app):
        self.app = app
        self.downloads_list = None
    
    def build(self) -> ft.Column:
        """Build the downloads UI"""
        # Header with stats
        self.stats_row = ft.Row(
            controls=[
                ft.Text("Downloads", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.TextButton("Pause All", icon=ft.Icons.PAUSE, on_click=self._on_pause_all),
                ft.TextButton("Resume All", icon=ft.Icons.PLAY_ARROW, on_click=self._on_resume_all),
                ft.TextButton("Clear Completed", icon=ft.Icons.CLEAR_ALL, on_click=self._on_clear_completed),
            ]
        )
        
        # Downloads list
        self.downloads_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
        )
        
        # Load existing downloads
        self._refresh_downloads()
        
        return ft.Column(
            controls=[
                self.stats_row,
                self.downloads_list,
            ],
            expand=True,
        )
    
    def _refresh_downloads(self):
        """Refresh downloads list from database"""
        if not self.app or not self.app.db_manager:
            return
        
        self.downloads_list.controls.clear()
        
        # Get pending and downloading items
        pending = self.app.db_manager.get_downloads(status='pending')
        downloading = self.app.db_manager.get_downloads(status='downloading')
        completed = self.app.db_manager.get_downloads(status='completed')
        failed = self.app.db_manager.get_downloads(status='failed')
        
        # Add downloading items first
        for item in downloading:
            self.downloads_list.controls.append(self._create_download_item(item, is_active=True))
        
        # Add pending items
        for item in pending:
            self.downloads_list.controls.append(self._create_download_item(item, is_active=False))
        
        # Add completed items (collapsed by default)
        if completed:
            self.downloads_list.controls.append(
                ft.Divider(height=30, thickness=1)
            )
            self.downloads_list.controls.append(
                ft.Text("Completed", size=16, weight=ft.FontWeight.BOLD)
            )
            for item in completed[:5]:  # Show last 5
                self.downloads_list.controls.append(self._create_download_item(item, is_completed=True))
        
        # Add failed items
        if failed:
            self.downloads_list.controls.append(
                ft.Divider(height=30, thickness=1)
            )
            self.downloads_list.controls.append(
                ft.Text("Failed", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.RED)
            )
            for item in failed[:5]:  # Show last 5
                self.downloads_list.controls.append(self._create_download_item(item, is_failed=True))
        
        if self.downloads_list.page:
            self.downloads_list.page.update()
    
    def _create_download_item(self, download: Dict, is_active: bool = False, 
                               is_completed: bool = False, is_failed: bool = False) -> ft.Container:
        """Create a download list item"""
        manga_title = download.get('manga_title', 'Unknown')
        chapter_name = download.get('chapter_name', '')
        progress = download.get('progress', 0.0)
        status = download.get('status', 'pending')
        speed = download.get('speed', 0.0)
        
        # Status color
        if is_completed:
            status_color = ft.colors.GREEN
            status_icon = ft.Icons.CHECK_CIRCLE
        elif is_failed:
            status_color = ft.colors.RED
            status_icon = ft.Icons.ERROR
        else:
            status_color = ft.colors.BLUE
            status_icon = ft.Icons.DOWNLOADING
        
        # Progress bar
        progress_bar = ft.ProgressBar(
            value=progress / 100 if progress else 0,
            width=400,
            color=status_color,
        )
        
        # Speed text
        speed_text = f"{speed:.1f} ch/s" if speed > 0 else ""
        
        # Controls based on status
        controls = []
        if is_active:
            controls.append(
                ft.IconButton(
                    icon=ft.Icons.PAUSE,
                    tooltip="Pause",
                    data=download['id'],
                    on_click=self._on_pause
                )
            )
            controls.append(
                ft.IconButton(
                    icon=ft.Icons.CANCEL,
                    tooltip="Cancel",
                    data=download['id'],
                    on_click=self._on_cancel
                )
            )
        elif status == 'paused':
            controls.append(
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    tooltip="Resume",
                    data=download['id'],
                    on_click=self._on_resume
                )
            )
            controls.append(
                ft.IconButton(
                    icon=ft.Icons.CANCEL,
                    tooltip="Cancel",
                    data=download['id'],
                    on_click=self._on_cancel
                )
            )
        elif is_failed:
            controls.append(
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Retry",
                    data=download['id'],
                    on_click=self._on_retry
                )
            )
            controls.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Remove",
                    data=download['id'],
                    on_click=self._on_remove
                )
            )
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(status_icon, color=status_color),
                    ft.Column(
                        controls=[
                            ft.Text(manga_title, size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(chapter_name, size=12, color=ft.colors.GREY),
                            ft.Row(
                                controls=[
                                    progress_bar,
                                    ft.Text(f"{progress:.0f}%", size=12, width=40),
                                    ft.Text(speed_text, size=12, width=80),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Row(controls=controls, spacing=0),
                ],
                spacing=10,
            ),
            padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=5,
        )
    
    def _on_pause_all(self, e):
        """Pause all active downloads"""
        if self.app and self.app.download_manager:
            for task in self.app.download_manager.get_active_downloads():
                self.app.download_manager.pause_download(task.id)
            self._refresh_downloads()
    
    def _on_resume_all(self, e):
        """Resume all paused downloads"""
        if self.app and self.app.download_manager:
            # TODO: Get paused downloads and resume
            self._refresh_downloads()
    
    def _on_clear_completed(self, e):
        """Clear completed downloads"""
        if self.app and self.app.db_manager:
            completed = self.app.db_manager.get_downloads(status='completed')
            for item in completed:
                self.app.db_manager.delete_download(item['id'])
            self._refresh_downloads()
    
    def _on_pause(self, e):
        """Pause a specific download"""
        download_id = int(e.control.data)
        if self.app and self.app.download_manager:
            self.app.download_manager.pause_download(download_id)
            self._refresh_downloads()
    
    def _on_resume(self, e):
        """Resume a paused download"""
        download_id = int(e.control.data)
        if self.app and self.app.download_manager:
            self.app.download_manager.resume_download(download_id)
            self._refresh_downloads()
    
    def _on_cancel(self, e):
        """Cancel a download"""
        download_id = int(e.control.data)
        if self.app and self.app.download_manager:
            self.app.download_manager.cancel_download(download_id)
            self._refresh_downloads()
    
    def _on_retry(self, e):
        """Retry a failed download"""
        download_id = int(e.control.data)
        # TODO: Implement retry logic
        self._refresh_downloads()
    
    def _on_remove(self, e):
        """Remove a download entry"""
        download_id = int(e.control.data)
        if self.app and self.app.db_manager:
            self.app.db_manager.delete_download(download_id)
            self._refresh_downloads()
    
    def update_progress(self, download_id: int, progress: float, speed: float):
        """Update progress for a specific download"""
        # Find and update the specific item
        # For now, just refresh the whole list
        self._refresh_downloads()
