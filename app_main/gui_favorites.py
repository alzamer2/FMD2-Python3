"""
FMD2 Python - Favorites View
Shows tracked manga with update checking and batch download
"""

import flet as ft
from typing import List, Dict, Optional


class FavoritesView:
    """
    Favorites view showing tracked manga series
    """
    
    def __init__(self, app):
        self.app = app
        self.favorites_list = None
    
    def build(self) -> ft.Column:
        """Build the favorites UI"""
        # Header with actions
        header_row = ft.Row(
            controls=[
                ft.Text("Favorites", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Check Updates",
                    icon=ft.Icons.REFRESH,
                    on_click=self._on_check_updates
                ),
                ft.ElevatedButton(
                    "Download New",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=self._on_download_new
                ),
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    tooltip="Add Favorite",
                    on_click=self._on_add_favorite
                ),
            ]
        )
        
        # Filter row
        self.filter_dropdown = ft.Dropdown(
            label="Filter",
            width=150,
            options=[
                ft.dropdown.Option("all", "All"),
                ft.dropdown.Option("has_new", "Has New Chapters"),
                ft.dropdown.Option("completed", "Completed"),
                ft.dropdown.Option("ongoing", "Ongoing"),
            ],
            value="all",
        )
        # Assign event handler after initialization
        self.filter_dropdown.on_change = self._on_filter_change
        
        # Favorites list
        self.favorites_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
        )
        
        # Load favorites
        self._refresh_favorites()
        
        return ft.Column(
            controls=[
                header_row,
                ft.Row(controls=[self.filter_dropdown]),
                self.favorites_list,
            ],
            expand=True,
        )
    
    def _refresh_favorites(self):
        """Refresh favorites list from database"""
        if not self.app or not self.app.db_manager:
            return
        
        self.favorites_list.controls.clear()
        
        # Get favorites based on filter
        filter_value = self.filter_dropdown.value if self.filter_dropdown else "all"
        
        favorites = self.app.db_manager.get_favorites(enabled_only=(filter_value != "all"))
        
        for fav in favorites:
            # Apply filter
            if filter_value == "has_new" and fav.get('new_chapters_count', 0) == 0:
                continue
            
            self.favorites_list.controls.append(self._create_favorite_item(fav))
        
        if self.favorites_list.page:
            self.favorites_list.page.update()
    
    def _create_favorite_item(self, favorite: Dict) -> ft.Container:
        """Create a favorite list item"""
        title = favorite.get('title', 'Unknown')
        site_name = favorite.get('site_name', '')
        last_chapter = favorite.get('last_chapter', 'N/A')
        new_count = favorite.get('new_chapters_count', 0)
        cover_url = favorite.get('cover_url', '')
        enabled = favorite.get('enabled', True)
        
        # Highlight if new chapters available
        bgcolor = None
        if new_count > 0:
            bgcolor = ft.colors.BLUE_GREY_100
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Cover image placeholder
                    ft.Container(
                        width=60,
                        height=80,
                        bgcolor=ft.colors.GREY_300,
                        border_radius=5,
                        content=ft.Icon(ft.Icons.MENU_BOOK, size=40) if not cover_url else None,
                    ),
                    
                    # Info column
                    ft.Column(
                        controls=[
                            ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(site_name, size=12, color=ft.colors.GREY),
                            ft.Row(
                                controls=[
                                    ft.Text(f"Last: {last_chapter}", size=12),
                                    ft.Container(
                                        content=ft.Text(f"+{new_count} new", size=12, color=ft.colors.WHITE),
                                        bgcolor=ft.colors.GREEN,
                                        padding=5,
                                        border_radius=10,
                                        visible=new_count > 0,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    
                    # Actions
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                tooltip="Download New",
                                data=favorite['manga_url'],
                                on_click=self._on_download,
                                visible=new_count > 0,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.INFO_OUTLINE,
                                tooltip="Info",
                                data=favorite['manga_url'],
                                on_click=self._on_info,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE if not enabled else ft.Icons.REMOVE_CIRCLE,
                                tooltip="Remove" if enabled else "Disable",
                                data=favorite['manga_url'],
                                on_click=self._on_remove_or_disable,
                            ),
                        ],
                    ),
                ],
                spacing=10,
            ),
            padding=10,
            bgcolor=bgcolor,
            border_radius=5,
        )
    
    def _on_check_updates(self, e):
        """Check all favorites for updates"""
        if not self.app or not self.app.module_loader:
            return
        
        # Show loading indicator
        self._show_loading(True)
        
        # Check updates in background
        import threading
        threading.Thread(target=self._check_updates_thread, daemon=True).start()
    
    def _check_updates_thread(self):
        """Background thread to check for updates"""
        try:
            favorites = self.app.db_manager.get_favorites(enabled_only=True)
            
            for fav in favorites:
                # Find module for this favorite
                module = self.app.module_loader.find_module_for_url(fav['manga_url'])
                if module:
                    # TODO: Call module to check for new chapters
                    pass
            
            # Refresh UI
            self._show_loading(False)
            self._refresh_favorites()
            
        except Exception as e:
            print(f"Error checking updates: {e}")
            self._show_loading(False)
    
    def _on_download_new(self, e):
        """Download new chapters for all favorites"""
        if not self.app or not self.app.download_manager:
            return
        
        # TODO: Implement batch download of new chapters
        pass
    
    def _on_add_favorite(self, e):
        """Open dialog to add new favorite"""
        if not self.favorites_list.page:
            return
        
        # Create dialog
        url_field = ft.TextField(
            label="Manga URL",
            hint_text="Paste manga URL here...",
            expand=True,
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("Add Favorite"),
            content=ft.Column(
                controls=[
                    ft.Text("Enter the URL of the manga you want to track:"),
                    url_field,
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog()),
                ft.TextButton("Add", on_click=lambda e: self._add_favorite(url_field.value)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.favorites_list.page.dialog = dialog
        dialog.open = True
        self.favorites_list.page.update()
    
    def _close_dialog(self):
        """Close current dialog"""
        if self.favorites_list.page and self.favorites_list.page.dialog:
            self.favorites_list.page.dialog.open = False
            self.favorites_list.page.dialog = None
            self.favorites_list.page.update()
    
    def _add_favorite(self, url: str):
        """Add a favorite from URL"""
        self._close_dialog()
        
        if not url or not self.app or not self.app.module_loader:
            return
        
        # Find module for URL
        module = self.app.module_loader.find_module_for_url(url)
        if module:
            # TODO: Get manga info and add to favorites
            self.app.db_manager.add_favorite(
                site_id=module.id or module.name,
                site_name=module.name,
                manga_url=url,
                title="Loading..."
            )
            self._refresh_favorites()
        else:
            # Show error
            if self.favorites_list.page:
                self.favorites_list.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Could not recognize this URL")
                )
                self.favorites_list.page.snack_bar.open = True
                self.favorites_list.page.update()
    
    def _on_download(self, e):
        """Download new chapters for a specific favorite"""
        manga_url = e.control.data
        # TODO: Implement download logic
        pass
    
    def _on_info(self, e):
        """Show manga info"""
        manga_url = e.control.data
        # TODO: Show manga details dialog
        pass
    
    def _on_remove_or_disable(self, e):
        """Remove or disable a favorite"""
        manga_url = e.control.data
        if self.app and self.app.db_manager:
            # Toggle enabled status or remove
            self.app.db_manager.remove_favorite(manga_url)
            self._refresh_favorites()
    
    def _on_filter_change(self, e):
        """Handle filter change"""
        self._refresh_favorites()
    
    def _show_loading(self, show: bool):
        """Show or hide loading indicator"""
        # TODO: Implement loading indicator
        pass
