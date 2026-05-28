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
        
        # Create tabs using Flet 0.85.2 API
        self.settings_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            length=5,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="General"),
                            ft.Tab(label="Downloads"),
                            ft.Tab(label="Network"),
                            ft.Tab(label="Appearance"),
                            ft.Tab(label="About"),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            general_settings,
                            download_settings,
                            network_settings,
                            gui_settings,
                            about_section,
                        ],
                    ),
                ],
            ),
            expand=True,
            on_change=self._on_tab_change,
        )
        
        return ft.Column(
            controls=[
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                self.settings_tabs,
            ],
            expand=True,
            spacing=20,
        )
    
    def _on_tab_change(self, e):
        """Handle tab change"""
        pass
    
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
                        on_select=self._on_setting_change,
                    ),
                    
                    # Check for updates
                    ft.Switch(
                        label="Check for updates on startup",
                        value=general.get('check_updates', True),
                        data='check_updates',
                        on_select=self._on_setting_change,
                    ),
                    
                    # Auto check favorites on startup
                    ft.Switch(
                        label="Auto-check favorites on startup",
                        value=general.get('auto_check_fav_startup', True),
                        data='auto_check_fav_startup',
                        on_select=self._on_setting_change,
                    ),
                    
                    # Auto check favorites interval
                    ft.Row(
                        controls=[
                            ft.Switch(
                                label="Auto-check favorites interval",
                                value=general.get('auto_check_fav_interval', False),
                                data='auto_check_fav_interval',
                                on_select=self._on_setting_change,
                            ),
                            ft.TextField(
                                label="Interval (minutes)",
                                value=str(general.get('auto_check_fav_interval_minutes', 60)),
                                data='auto_check_fav_interval_minutes',
                                keyboard_type=ft.KeyboardType.NUMBER,
                                width=120,
                                on_select=self._on_setting_change,
                            ),
                        ]
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
                    
                    # After download action
                    ft.Dropdown(
                        label="After all downloads complete",
                        width=250,
                        options=[
                            ft.dropdown.Option("nothing", "Do nothing"),
                            ft.dropdown.Option("exit", "Exit application"),
                            ft.dropdown.Option("poweroff", "Power off computer"),
                            ft.dropdown.Option("hibernate", "Hibernate computer"),
                            ft.dropdown.Option("update", "Check for updates"),
                        ],
                        value=general.get('after_download_action', 'nothing'),
                        data='after_download_action',
                        on_select=self._on_setting_change,
                    ),
                    
                    # Delete completed tasks on close
                    ft.Switch(
                        label="Delete completed tasks on close",
                        value=general.get('delete_completed_tasks_on_close', False),
                        data='delete_completed_tasks_on_close',
                        on_select=self._on_setting_change,
                    ),
                    
                    # Sort downloads on new tasks
                    ft.Switch(
                        label="Sort downloads when adding new tasks",
                        value=general.get('sort_downloads_on_new_tasks', False),
                        data='sort_downloads_on_new_tasks',
                        on_select=self._on_setting_change,
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
                    
                    # Max parallel downloads
                    ft.TextField(
                        label="Max Parallel Downloads",
                        value=str(downloads.get('max_parallel', 1)),
                        data='max_parallel',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_select=self._on_setting_change,
                        helper_text="Number of simultaneous manga downloads",
                    ),
                    
                    # Max threads per download
                    ft.TextField(
                        label="Max Threads per Download",
                        value=str(downloads.get('max_threads', 1)),
                        data='max_threads',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_select=self._on_setting_change,
                        helper_text="Threads for each manga download",
                    ),
                    
                    # Max retries
                    ft.TextField(
                        label="Max Retries per Chapter",
                        value=str(downloads.get('max_retry', 5)),
                        data='max_retry',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_select=self._on_setting_change,
                    ),
                    
                    # Retry failed tasks
                    ft.TextField(
                        label="Retry Failed Tasks",
                        value=str(downloads.get('retry_failed_task', 1)),
                        data='retry_failed_task',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_select=self._on_setting_change,
                    ),
                    
                    # Always start from failed chapters
                    ft.Switch(
                        label="Always start from failed chapters",
                        value=downloads.get('always_start_from_failed', True),
                        data='always_start_from_failed',
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.Divider(),
                    
                    # Save format
                    ft.Dropdown(
                        label="Save Format",
                        width=250,
                        options=[
                            ft.dropdown.Option("cbz", "CBZ (Comic Book ZIP)"),
                            ft.dropdown.Option("zip", "ZIP Archive"),
                            ft.dropdown.Option("pdf", "PDF Document"),
                            ft.dropdown.Option("folder", "Folder (Raw Images)"),
                            ft.dropdown.Option("epub", "EPUB eBook"),
                        ],
                        value=downloads.get('save_format', 'cbz'),
                        data='save_format',
                        on_select=self._on_setting_change,
                    ),
                    
                    # PDF Quality
                    ft.Slider(
                        label="PDF Quality",
                        min=1,
                        max=100,
                        divisions=99,
                        value=downloads.get('pdf_quality', 95),
                        data='pdf_quality',
                        width=300,
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.Divider(),
                    
                    # Folder naming
                    ft.Switch(
                        label="Generate manga folder",
                        value=downloads.get('generate_manga_folder', False),
                        data='generate_manga_folder',
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.TextField(
                        label="Manga folder name pattern",
                        value=downloads.get('manga_custom_rename', '%MANGA%'),
                        data='manga_custom_rename',
                        expand=True,
                        on_select=self._on_setting_change,
                        helper_text="Use %MANGA% for manga name",
                    ),
                    
                    ft.Switch(
                        label="Generate chapter folder",
                        value=downloads.get('generate_chapter_folder', True),
                        data='generate_chapter_folder',
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.TextField(
                        label="Chapter folder name pattern",
                        value=downloads.get('chapter_custom_rename', '%CHAPTER%'),
                        data='chapter_custom_rename',
                        expand=True,
                        on_select=self._on_setting_change,
                        helper_text="Use %CHAPTER% for chapter name",
                    ),
                    
                    ft.TextField(
                        label="Filename pattern",
                        value=downloads.get('filename_custom_rename', '%FILENAME%'),
                        data='filename_custom_rename',
                        expand=True,
                        on_select=self._on_setting_change,
                        helper_text="Use %FILENAME% for image filename",
                    ),
                    
                    ft.Divider(),
                    
                    # Convert digits
                    ft.Row(
                        controls=[
                            ft.Switch(
                                label="Convert volume to digits",
                                value=downloads.get('convert_digit_volume', False),
                                data='convert_digit_volume',
                                on_select=self._on_setting_change,
                            ),
                            ft.TextField(
                                label="Volume digit length",
                                value=str(downloads.get('convert_digit_volume_length', 2)),
                                data='convert_digit_volume_length',
                                keyboard_type=ft.KeyboardType.NUMBER,
                                width=100,
                                on_select=self._on_setting_change,
                            ),
                        ]
                    ),
                    
                    ft.Row(
                        controls=[
                            ft.Switch(
                                label="Convert chapter to digits",
                                value=downloads.get('convert_digit_chapter', False),
                                data='convert_digit_chapter',
                                on_select=self._on_setting_change,
                            ),
                            ft.TextField(
                                label="Chapter digit length",
                                value=str(downloads.get('convert_digit_chapter_length', 3)),
                                data='convert_digit_chapter_length',
                                keyboard_type=ft.KeyboardType.NUMBER,
                                width=100,
                                on_select=self._on_setting_change,
                            ),
                        ]
                    ),
                    
                    ft.Divider(),
                    
                    # Image conversion
                    ft.Switch(
                        label="Convert PNG to JPEG",
                        value=downloads.get('png_save_as_jpeg', False),
                        data='png_save_as_jpeg',
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.Dropdown(
                        label="WebP save as",
                        width=200,
                        options=[
                            ft.dropdown.Option("0", "Keep as WebP"),
                            ft.dropdown.Option("1", "Convert to PNG"),
                            ft.dropdown.Option("2", "Convert to JPEG"),
                        ],
                        value=str(downloads.get('webp_save_as', 1)),
                        data='webp_save_as',
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.TextField(
                        label="PNG compression level (1-9)",
                        value=str(downloads.get('png_compression_level', 1)),
                        data='png_compression_level',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=150,
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.TextField(
                        label="JPEG quality (1-100)",
                        value=str(downloads.get('jpeg_quality', 80)),
                        data='jpeg_quality',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=150,
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.Divider(),
                    
                    # Download path
                    ft.TextField(
                        label="Download Location",
                        value=downloads.get('download_path', ''),
                        data='download_path',
                        expand=True,
                        on_select=self._on_setting_change,
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
                    
                    # Connection timeout
                    ft.TextField(
                        label="Connection Timeout (seconds)",
                        value=str(network.get('connection_timeout', 30)),
                        data='connection_timeout',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_select=self._on_setting_change,
                    ),
                    
                    # Max favorite threads
                    ft.TextField(
                        label="Max Favorite Check Threads",
                        value=str(network.get('max_favorite_threads', 1)),
                        data='max_favorite_threads',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_select=self._on_setting_change,
                    ),
                    
                    # Max update list threads
                    ft.TextField(
                        label="Max Update List Threads",
                        value=str(network.get('max_update_list_threads', 1)),
                        data='max_update_list_threads',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_select=self._on_setting_change,
                    ),
                    
                    # Max background load threads
                    ft.TextField(
                        label="Max Background Load Threads",
                        value=str(network.get('max_background_load_threads', 1)),
                        data='max_background_load_threads',
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.Divider(),
                    
                    # Use GZip
                    ft.Switch(
                        label="Use GZip compression",
                        value=network.get('use_gzip', True),
                        data='use_gzip',
                        on_select=self._on_setting_change,
                    ),
                    
                    # Cloudflare bypass
                    ft.Switch(
                        label="Enable Cloudflare bypass",
                        value=network.get('enable_cloudflare_bypass', True),
                        data='enable_cloudflare_bypass',
                        on_select=self._on_setting_change,
                    ),
                    
                    # Auto disable cloudflare bypass
                    ft.Switch(
                        label="Auto-disable Cloudflare bypass on failure",
                        value=network.get('auto_disable_cloudflare_bypass', False),
                        data='auto_disable_cloudflare_bypass',
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.Divider(),
                    
                    # Proxy settings
                    ft.TextField(
                        label="Proxy URL (optional)",
                        hint_text="http://proxy:port",
                        value=network.get('proxy', ''),
                        data='proxy',
                        expand=True,
                        on_select=self._on_setting_change,
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
                        on_select=self._on_setting_change,
                    ),
                    
                    # Compact mode
                    ft.Switch(
                        label="Compact Mode",
                        value=gui.get('compact_mode', False),
                        data='compact_mode',
                        on_select=self._on_setting_change,
                    ),
                    
                    ft.Divider(),
                    
                    # Show balloon hints
                    ft.Switch(
                        label="Show notification balloons",
                        value=gui.get('show_balloon_hint', True),
                        data='show_balloon_hint',
                        on_select=self._on_setting_change,
                    ),
                    
                    # Show favorites tab on new manga
                    ft.Switch(
                        label="Switch to favorites tab when new chapters found",
                        value=gui.get('show_favorites_tab_on_new_manga', False),
                        data='show_favorites_tab_on_new_manga',
                        on_select=self._on_setting_change,
                    ),
                    
                    # Show downloads tab on new tasks
                    ft.Switch(
                        label="Switch to downloads tab on new tasks",
                        value=gui.get('show_downloads_tab_on_new_tasks', True),
                        data='show_downloads_tab_on_new_tasks',
                        on_select=self._on_setting_change,
                    ),
                    
                    # Enable load cover
                    ft.Switch(
                        label="Load and display cover images",
                        value=gui.get('enable_load_cover', False),
                        data='enable_load_cover',
                        on_select=self._on_setting_change,
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
                        color=ft.Colors.GREY,
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
        general_settings = ['one_instance_only', 'check_updates', 'language', 
                           'auto_check_fav_startup', 'auto_check_fav_interval', 
                           'auto_check_fav_interval_minutes', 'after_download_action',
                           'delete_completed_tasks_on_close', 'sort_downloads_on_new_tasks']
        download_settings = ['max_parallel', 'max_threads', 'max_retry', 'retry_failed_task',
                            'always_start_from_failed', 'save_format', 'pdf_quality',
                            'generate_manga_folder', 'manga_custom_rename', 
                            'generate_chapter_folder', 'chapter_custom_rename',
                            'filename_custom_rename', 'convert_digit_volume', 
                            'convert_digit_volume_length', 'convert_digit_chapter',
                            'convert_digit_chapter_length', 'png_save_as_jpeg',
                            'webp_save_as', 'png_compression_level', 'jpeg_quality',
                            'download_path']
        network_settings = ['connection_timeout', 'max_favorite_threads', 
                           'max_update_list_threads', 'max_background_load_threads',
                           'use_gzip', 'enable_cloudflare_bypass', 
                           'auto_disable_cloudflare_bypass', 'proxy']
        gui_settings = ['theme', 'compact_mode', 'show_balloon_hint',
                       'show_favorites_tab_on_new_manga', 'show_downloads_tab_on_new_tasks',
                       'enable_load_cover']
        
        if data in general_settings:
            section = 'general'
        elif data in download_settings:
            section = 'downloads'
        elif data in network_settings:
            section = 'network'
        elif data in gui_settings:
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
        elif isinstance(control, ft.Slider):
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
