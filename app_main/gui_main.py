"""
FMD2 Python - Main Navigation View
Tab-based navigation with Search, Favorites, Downloads, and Settings
"""

import flet as ft
from typing import Optional


class MainNavigationView:
    """
    Main navigation view with rail for desktop/web
    Bottom navigation bar for mobile
    """
    
    def __init__(self, search_view, downloads_view, favorites_view, settings_view):
        self.search_view = search_view
        self.downloads_view = downloads_view
        self.favorites_view = favorites_view
        self.settings_view = settings_view
        
        self.current_index = 0
        self.content_area = None
    
    def build(self) -> ft.Column:
        """Build the main navigation UI"""
        # Create content area
        self.content_area = ft.Container(
            expand=True,
            content=self.search_view.build()
        )
        
        # Create navigation rail for desktop
        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            leading=ft.FloatingActionButton(
                icon=ft.icons.ADD, 
                label=ft.Text("New"),
                on_click=self._on_new_click
            ),
            group_alignment=-0.95,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.SEARCH_OUTLINED,
                    selected_icon=ft.icons.SEARCH,
                    label=ft.Text("Search")
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.FAVORITE_BORDER,
                    selected_icon=ft.icons.FAVORITE,
                    label=ft.Text("Favorites")
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.DOWNLOAD_OUTLINED,
                    selected_icon=ft.icons.DOWNLOAD,
                    label=ft.Text("Downloads")
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label=ft.Text("Settings")
                ),
            ],
            on_change=self._on_nav_change,
        )
        
        # Main layout
        return ft.Row(
            expand=True,
            controls=[
                nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
        )
    
    def _on_nav_change(self, e):
        """Handle navigation change"""
        self.current_index = e.control.selected_index
        
        # Update content based on selection
        if self.current_index == 0:
            self.content_area.content = self.search_view.build()
        elif self.current_index == 1:
            self.content_area.content = self.favorites_view.build()
        elif self.current_index == 2:
            self.content_area.content = self.downloads_view.build()
        elif self.current_index == 3:
            self.content_area.content = self.settings_view.build()
        
        self.content_area.update()
    
    def _on_new_click(self, e):
        """Handle new download/favorite button click"""
        # Navigate to search and focus on search box
        e.page.navigation_rail.selected_index = 0
        self.search_view.focus_search()
    
    def switch_to_downloads(self):
        """Switch to downloads tab"""
        self.content_area.content = self.downloads_view.build()
        self.content_area.update()
    
    def switch_to_favorites(self):
        """Switch to favorites tab"""
        self.content_area.content = self.favorites_view.build()
        self.content_area.update()
