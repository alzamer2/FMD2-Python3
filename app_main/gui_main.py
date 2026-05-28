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
        # Create content area first (will be updated when tabs change)
        self.content_area = ft.Container(
            expand=True,
            content=self.downloads_view.build()
        )
        
        # Create TabBar with tabs - TabBar handles the tab buttons
        self.tab_bar = ft.TabBar(
            tabs=[
                ft.Tab(label="Downloads", icon=ft.Icons.DOWNLOAD_OUTLINED),
                ft.Tab(label="Manga Info", icon=ft.Icons.SEARCH_OUTLINED),
                ft.Tab(label="Favorites", icon=ft.Icons.FAVORITE_BORDER),
                ft.Tab(label="Settings", icon=ft.Icons.SETTINGS_OUTLINED),
            ],
            on_click=self._on_nav_click,
        )
        self.tab_bar.selected_index = 0
        
        return ft.Column(
            controls=[
                self.tab_bar,
                self.content_area,
            ],
            expand=True,
            spacing=0,
        )
    
    def _on_nav_click(self, e):
        """Handle navigation tab click"""
        # Get the clicked tab index by finding it in the tabs list
        clicked_tab = e.control
        self.current_index = clicked_tab.selected_index
        
        # Update content based on selected index
        if self.current_index == 0:
            self.content_area.content = self.downloads_view.build()
        elif self.current_index == 1:
            self.content_area.content = self.search_view.build()
        elif self.current_index == 2:
            self.content_area.content = self.favorites_view.build()
            self.favorites_view.did_mount()
        elif self.current_index == 3:
            self.content_area.content = self.settings_view.build()
        
        self.content_area.update()
    
    def _on_new_click(self, e):
        """Handle new download/favorite button click"""
        # Navigate to manga info (search) tab
        self.current_index = 1
        self.tab_bar.selected_index = 1
        self.content_area.content = self.search_view.build()
        self.content_area.update()
        self.search_view.focus_search()
    
    def switch_to_downloads(self):
        """Switch to downloads tab"""
        self.current_index = 0
        self.tab_bar.selected_index = 0
        self.content_area.content = self.downloads_view.build()
        self.content_area.update()
    
    def switch_to_favorites(self):
        """Switch to favorites tab"""
        self.current_index = 2
        self.tab_bar.selected_index = 2
        self.content_area.content = self.favorites_view.build()
        self.favorites_view.did_mount()
        self.content_area.update()
