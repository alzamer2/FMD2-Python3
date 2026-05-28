"""
FMD2 Python - Main Navigation View
Tab-based navigation with Downloads, Search, Favorites, and Settings
"""

import flet as ft
from typing import Optional


class MainNavigationView:
    """
    Main navigation view with top tabs
    """
    
    def __init__(self, search_view, downloads_view, favorites_view, settings_view):
        self.search_view = search_view
        self.downloads_view = downloads_view
        self.favorites_view = favorites_view
        self.settings_view = settings_view
        
        self.current_index = 0
        self.content_area = None
        self.tab_bar = None  # Store reference to tab bar
    
    def build(self) -> ft.Column:
        """Build the main navigation UI"""
        # Content area that changes based on selected tab
        self.content_area = ft.Container(
            content=self.downloads_view.build(),
            expand=True,
        )
        
        # Create tabs WITHOUT content (Flet 0.85+ compatibility)
        self.tabs_control = ft.Tabs(
            selected_index=0,
            animation_duration=200,
            tabs=[
                ft.Tab(text="Downloads", icon=ft.Icons.DOWNLOAD_OUTLINED),
                ft.Tab(text="Manga Info", icon=ft.Icons.SEARCH_OUTLINED),
                ft.Tab(text="Favorites", icon=ft.Icons.FAVORITE_BORDER),
                ft.Tab(text="Settings", icon=ft.Icons.SETTINGS_OUTLINED),
            ],
            expand=True,
            on_change=self._on_nav_change,
        )
        
        return ft.Column(
            controls=[self.tabs_control, self.content_area],
            expand=True,
            spacing=0,
        )
    
    def _on_nav_change(self, e):
        """Handle navigation tab change"""
        self.current_index = e.control.selected_index
        
        # Update content based on selected tab
        if self.current_index == 0:
            self.content_area.content = self.downloads_view.build()
        elif self.current_index == 1:
            self.content_area.content = self.search_view.build()
        elif self.current_index == 2:
            self.content_area.content = self.favorites_view.build()
            # Trigger did_mount for favorites when switching to it
            self.favorites_view.did_mount()
        elif self.current_index == 3:
            self.content_area.content = self.settings_view.build()
        
        self.content_area.update()
    
    def _on_new_click(self, e):
        """Handle new download/favorite button click"""
        # Navigate to manga info (search) tab
        self.current_index = 1
        self.tabs_control.selected_index = 1
        self.tabs_control.update()
        self.search_view.focus_search()
    
    def switch_to_downloads(self):
        """Switch to downloads tab"""
        self.current_index = 0
        self.tabs_control.selected_index = 0
        self.tabs_control.update()
    
    def switch_to_favorites(self):
        """Switch to favorites tab"""
        self.current_index = 2
        self.tabs_control.selected_index = 2
        self.tabs_control.update()
        self.favorites_view.did_mount()
