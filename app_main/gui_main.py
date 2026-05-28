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
        # Create tabs with content directly
        self.tabs_control = ft.Tabs(
            selected_index=0,
            animation_duration=200,
            tabs=[
                ft.Tab(
                    label="Downloads",
                    icon=ft.Icons.DOWNLOAD_OUTLINED,
                    content=self.downloads_view.build(),
                ),
                ft.Tab(
                    label="Manga Info",
                    icon=ft.Icons.SEARCH_OUTLINED,
                    content=self.search_view.build(),
                ),
                ft.Tab(
                    label="Favorites",
                    icon=ft.Icons.FAVORITE_BORDER,
                    content=self.favorites_view.build(),
                ),
                ft.Tab(
                    label="Settings",
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    content=self.settings_view.build(),
                ),
            ],
            expand=True,
            on_change=self._on_nav_change,
        )
        
        return ft.Column(
            controls=[self.tabs_control],
            expand=True,
            spacing=0,
        )
    
    def _on_nav_change(self, e):
        """Handle navigation tab change"""
        self.current_index = e.control.selected_index
        
        # Trigger did_mount for favorites when switching to it
        if self.current_index == 2:
            self.favorites_view.did_mount()
    
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
