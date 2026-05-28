"""
FMD2 Python - Settings View
Application settings and configuration
"""

import flet as ft
import json
from typing import Dict, Any


class SettingsView:
    """
    Settings view for application configuration
    """
    
    def __init__(self, app):
        self.app = app
        self.settings_tabs = None
    
    def build(self) -> ft.Column:
        """Build the settings UI"""
        # General settings
        general_settings = self._build_general_settings()
        
        # Download settings
        download_settings = self._build_download_settings()
        
        # Network settings
        network_settings = self._build_network_settings()
        
        # GUI settings
        gui_settings = self._build_gui_settings()
        
        # About section
        about_section = self._build_about_section()
        
        # Create tabs
        self.settings_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="General", content=general_settings),
                ft.Tab(text="Downloads", content=download_settings),
                ft.Tab(text="Network", content=network_settings),
                ft.Tab(text="Appearance", content=gui_settings),
                ft.Tab(text="About", content=about_section),
            ],
            expand=True,
        )
        
        return ft.Column(
            controls=[
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                self.settings_tabs,
            ],
            expand=True,
            spacing=20,
        )
    
    def _build_general_settings(self) -> ft.Container:
        """Build general settings tab"""
        config = self.app.config if self.app else {}
        general = config.get('general', {})
        
        return ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("General Settings", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    # One instance only
                    ft.Switch(
                        label="One instance only",
                        value=general.get('one_instance_only', True),
                        data='one_instance_only',
                        on_change=self._on_setting_change,
                    ),
                    
                    # Check for updates
                    ft.Switch(
                        label="Check for updates on startup",
                        value=general.get('check_updates', True),
                        data='check_updates',
                        on_change=self._on_setting_change,
                    ),
                    
                    # Language selector
                    ft.Dropdown(
                        label="Language",
                        width=200,
                        options=[
                            ft.dropdown.Option("en", "English"),
                            ft.dropdown.Option("es", "Español"),
                            ft.dropdown.Option("fr", "Français"),
                            ft.dropdown.Option("de", "Deutsch"),
                            ft.dropdown.Option("it", "Italiano"),
                            ft.dropdown.Option("pt", "Português"),
                            ft.dropdown.Option("ru", "Русский"),
                            ft.dropdown.Option("ja", "日本語"),
                            ft.dropdown.Option("ko", "한국어"),
                            ft.dropdown.Option("zh", "中文"),
                        ],
                        value=general.get('language', 'en'),
                        data='language',
                    ),
                    
                    ft.Divider(),
                    
                    # Buttons
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Save Changes",
                                icon=ft.Icons.SAVE,
                                on_click=self._on_save_settings,
                            ),
                            ft.ElevatedButton(
                                "Reset to Defaults",
                                icon=ft.Icons.UNDO,
                                on_click=self._on_reset_defaults,
                            ),
                        ]
                    ),
                ],
                spacing=15,
            ),
        )
    
    def _build_download_settings(self) -> ft.Container:
        """Build download settings tab"""
        config = self.app.config if self.app else {}
        downloads = config.get('downloads', {})
        
        return ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Download Settings", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    # Max concurrent downloads
                    ft.TextField(
                        label="Max Concurrent Downloads",
                        value=str(downloads.get('max_concurrent', 3)),
                        data='max_concurrent',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_change=self._on_setting_change,
                    ),
                    
                    # Retry count
                    ft.TextField(
                        label="Max Retries per Download",
                        value=str(downloads.get('retry_count', 3)),
                        data='retry_count',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_change=self._on_setting_change,
                    ),
                    
                    # Save format
                    ft.Dropdown(
                        label="Save Format",
                        width=200,
                        options=[
                            ft.dropdown.Option("cbz", "CBZ (Comic Book ZIP)"),
                            ft.dropdown.Option("zip", "ZIP"),
                            ft.dropdown.Option("pdf", "PDF"),
                            ft.dropdown.Option("folder", "Folder (Images)"),
                        ],
                        value=downloads.get('save_format', 'cbz'),
                        data='save_format',
                    ),
                    
                    # Download path
                    ft.TextField(
                        label="Download Location",
                        value=downloads.get('download_path', ''),
                        data='download_path',
                        expand=True,
                        on_change=self._on_setting_change,
                        suffix=ft.IconButton(
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=self._on_browse_folder,
                        ),
                    ),
                ],
                spacing=15,
            ),
        )
    
    def _build_network_settings(self) -> ft.Container:
        """Build network settings tab"""
        config = self.app.config if self.app else {}
        network = config.get('network', {})
        
        return ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Network Settings", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    # Proxy settings
                    ft.TextField(
                        label="Proxy URL (optional)",
                        hint_text="http://proxy:port",
                        value=network.get('proxy', ''),
                        data='proxy',
                        expand=True,
                        on_change=self._on_setting_change,
                    ),
                    
                    # Timeout
                    ft.TextField(
                        label="Request Timeout (seconds)",
                        value=str(network.get('timeout', 30)),
                        data='timeout',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_change=self._on_setting_change,
                    ),
                    
                    ft.Divider(),
                    
                    # Test connection button
                    ft.ElevatedButton(
                        "Test Connection",
                        icon=ft.Icons.WIFI,
                        on_click=self._on_test_connection,
                    ),
                ],
                spacing=15,
            ),
        )
    
    def _build_gui_settings(self) -> ft.Container:
        """Build GUI/Appearance settings tab"""
        config = self.app.config if self.app else {}
        gui = config.get('gui', {})
        
        return ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Appearance Settings", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    # Theme selector
                    ft.RadioGroup(
                        ft.Column(
                            controls=[
                                ft.Radio(value="system", label="System Default"),
                                ft.Radio(value="light", label="Light"),
                                ft.Radio(value="dark", label="Dark"),
                            ]
                        ),
                        value=gui.get('theme', 'system'),
                        data='theme',
                        on_change=self._on_setting_change,
                    ),
                    
                    # Compact mode
                    ft.Switch(
                        label="Compact Mode",
                        value=gui.get('compact_mode', False),
                        data='compact_mode',
                        on_change=self._on_setting_change,
                    ),
                    
                    ft.Divider(),
                    
                    # Apply theme button
                    ft.ElevatedButton(
                        "Apply Theme",
                        icon=ft.Icons.PALETTE,
                        on_click=self._on_apply_theme,
                    ),
                ],
                spacing=15,
            ),
        )
    
    def _build_about_section(self) -> ft.Container:
        """Build about section"""
        return ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("About FMD2 Python", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    ft.Text(
                        "Free Manga Downloader 2 (Python Port)\n\n"
                        "A modern rewrite of the classic FMD2 application using Python and Flet.\n\n"
                        "Features:\n"
                        "- 600+ manga site support via Lua modules\n"
                        "- Multi-threaded downloads\n"
                        "- Favorites tracking\n"
                        "- Cross-platform (Desktop, Web, Mobile)\n\n"
                        "Original FMD2 by dazedcat19\n"
                        "Python Port © 2024",
                        size=14,
                    ),
                    
                    ft.Divider(),
                    
                    # Check for updates button
                    ft.ElevatedButton(
                        "Check for Updates",
                        icon=ft.Icons.UPDATE,
                        on_click=self._on_check_updates,
                    ),
                    
                    ft.Text(
                        "Version: 2.0.0 (Python)",
                        size=12,
                        color=ft.colors.GREY,
                    ),
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
    
    def _on_setting_change(self, e):
        """Handle setting change"""
        # Update config in memory
        if not self.app:
            return
        
        control = e.control
        data = getattr(control, 'data', None)
        
        if not data:
            return
        
        # Determine which section
        if data in ['one_instance_only', 'check_updates', 'language']:
            section = 'general'
        elif data in ['max_concurrent', 'retry_count', 'save_format', 'download_path']:
            section = 'downloads'
        elif data in ['proxy', 'timeout']:
            section = 'network'
        elif data in ['theme', 'compact_mode']:
            section = 'gui'
        else:
            return
        
        # Get value
        if isinstance(control, ft.Switch):
            value = control.value
        elif isinstance(control, ft.TextField):
            value = control.value
        elif isinstance(control, ft.Dropdown):
            value = control.value
        elif isinstance(control, ft.RadioGroup):
            value = control.value
        else:
            return
        
        # Update config
        if section not in self.app.config:
            self.app.config[section] = {}
        
        self.app.config[section][data] = value
    
    def _on_save_settings(self, e):
        """Save settings to file"""
        if self.app:
            self.app.save_config()
            
            # Show confirmation
            if self.settings_tabs.page:
                self.settings_tabs.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Settings saved successfully!")
                )
                self.settings_tabs.page.snack_bar.open = True
                self.settings_tabs.page.update()
    
    def _on_reset_defaults(self, e):
        """Reset settings to defaults"""
        if self.app:
            self.app.config = self.app.get_default_config()
            self.app.save_config()
            
            # Refresh UI
            self.settings_tabs.page.update()
    
    def _on_browse_folder(self, e):
        """Open folder browser"""
        # TODO: Implement folder picker
        pass
    
    def _on_test_connection(self, e):
        """Test network connection"""
        # TODO: Implement connection test
        pass
    
    def _on_apply_theme(self, e):
        """Apply theme changes"""
        if self.settings_tabs.page and self.app:
            theme = self.app.config.get('gui', {}).get('theme', 'system')
            
            if theme == 'dark':
                self.settings_tabs.page.theme_mode = ft.ThemeMode.DARK
            elif theme == 'light':
                self.settings_tabs.page.theme_mode = ft.ThemeMode.LIGHT
            else:
                self.settings_tabs.page.theme_mode = ft.ThemeMode.SYSTEM
            
            self.settings_tabs.page.update()
    
    def _on_check_updates(self, e):
        """Check for application updates"""
        # TODO: Implement update checker
        pass
