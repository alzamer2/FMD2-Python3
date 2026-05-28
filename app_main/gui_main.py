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
        # Create tab definitions WITHOUT content
        self.tab_definitions = [
            ft.Tab(label="Downloads", icon=ft.Icons.DOWNLOAD_OUTLINED),
            ft.Tab(label="Manga Info", icon=ft.Icons.SEARCH_OUTLINED),
            ft.Tab(label="Favorites", icon=ft.Icons.FAVORITE_BORDER),
            ft.Tab(label="Settings", icon=ft.Icons.SETTINGS_OUTLINED),
        ]
        
        # Create TabBar (must be used within Tabs, but we'll use it with separate content)
        self.tab_bar = ft.TabBar(
            tabs=self.tab_definitions,
            on_click=self._on_nav_click,
        )
        self.tab_bar.selected_index = 0
        
        # Create content area
        self.content_area = ft.Container(
            expand=True,
            content=self.downloads_view.build()
        )
        
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
        # Get the index of the clicked tab
        clicked_tab = e.control
        if hasattr(clicked_tab, 'selected_index'):
            self.current_index = clicked_tab.selected_index
        else:
            # Fallback: find index from tab_definitions
            try:
                self.current_index = self.tab_definitions.index(clicked_tab)
            except ValueError:
                self.current_index = 0
        
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
