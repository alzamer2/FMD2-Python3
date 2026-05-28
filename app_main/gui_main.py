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
        self.tabs_control = None  # Store reference to tabs control
    
    def build(self) -> ft.Column:
        """Build the main navigation UI"""
        # Create tabs with content directly
        self.tabs_control = ft.Tabs(
            selected_index=0,
            on_change=self._on_nav_change,
            expand=True,
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
        )
        
        # Main layout
        return ft.Column(
            expand=True,
            controls=[self.tabs_control],
            spacing=0,
        )
    
    def _on_nav_change(self, e):
        """Handle navigation change"""
        # Get the selected index
        self.current_index = e.control.selected_index
        
        # Update views based on selection
        if self.current_index == 2:  # Favorites tab
            # Trigger refresh when switching to favorites
            self.favorites_view.did_mount()
        elif self.current_index == 0:  # Downloads tab
            # Trigger refresh when switching to downloads
            self.downloads_view.did_mount()
    
    def _on_new_click(self, e):
        """Handle new download/favorite button click"""
        # Navigate to manga info (search) tab
        if self.tabs_control:
            self.tabs_control.selected_index = 1
            self.tabs_control.update()
        self.search_view.focus_search()
    
    def switch_to_downloads(self):
        """Switch to downloads tab"""
        if self.tabs_control:
            self.tabs_control.selected_index = 0
            self.tabs_control.update()
    
    def switch_to_favorites(self):
        """Switch to favorites tab"""
        if self.tabs_control:
            self.tabs_control.selected_index = 2
            self.tabs_control.update()
