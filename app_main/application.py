"""
FMD2 Python - Free Manga Downloader 2 (Python Port)
Main Application Module
"""

import os
import sys
import json
import threading
from pathlib import Path

import flet as ft

# Import core modules
from app_main.lua_handler import LuaHandler
from app_main.module_loader import ModuleLoader
from app_main.fmd_crypto import FMDCrypto
from app_main.http_client import HTTPClient, CookieManager
from app_main.database_manager import DatabaseManager
from app_main.download_thread import DownloadManager
from app_main.clipboard_monitor import ClipboardMonitor
from app_main.tray_icon import TrayIconManager

# Import GUI modules
from app_main.gui_main import MainNavigationView
from app_main.gui_search import SearchView
from app_main.gui_downloads import DownloadsView
from app_main.gui_favorites import FavoritesView
from app_main.gui_settings import SettingsView


class FMD2Application:
    """Main FMD2 Application class"""
    
    def __init__(self, web_mode=False, mobile_mode=False, host='0.0.0.0', port=5000, debug=False):
        self.web_mode = web_mode
        self.mobile_mode = mobile_mode
        self.host = host
        self.port = port
        self.debug = debug
        
        # Get base directory
        self.base_dir = Path(__file__).parent.parent
        self.lua_dir = self.base_dir / 'lua'
        
        # Initialize core components
        self.lua_handler = None
        self.module_loader = None
        self.crypto = None
        self.http_client = None
        self.cookie_manager = None
        self.db_manager = None
        self.download_manager = None
        self.clipboard_monitor = None
        self.tray_icon = None
        
        # GUI state
        self.page = None
        self.current_view = None
        
        # Configuration
        self.config = {}
        self.config_file = self.base_dir / 'config.json'
        
        # Loaded modules
        self.loaded_modules = []
        
    def initialize(self):
        """Initialize all core components"""
        print("Initializing FMD2 Python...")
        
        # Load configuration
        self.load_config()
        
        # Initialize crypto module
        print("Initializing crypto module...")
        self.crypto = FMDCrypto()
        
        # Initialize cookie manager
        print("Initializing cookie manager...")
        self.cookie_manager = CookieManager(self.base_dir / 'cookies.txt')
        
        # Initialize HTTP client
        print("Initializing HTTP client...")
        self.http_client = HTTPClient(self.cookie_manager)
        
        # Initialize Lua handler
        print("Initializing Lua handler...")
        self.lua_handler = LuaHandler(
            lua_dir=self.lua_dir,
            crypto=self.crypto,
            http_client=self.http_client,
            dofile=os.environ.get('FMD_LUA_DOFILE', '0') == '1'
        )
        
        # Initialize module loader
        print("Loading Lua modules...")
        self.module_loader = ModuleLoader(self.lua_handler)
        self.loaded_modules = self.module_loader.load_all_modules()
        print(f"Loaded {len(self.loaded_modules)} modules")
        
        # Initialize database
        print("Initializing database...")
        self.db_manager = DatabaseManager(self.base_dir / 'fmd2.db')
        
        # Initialize download manager
        print("Initializing download manager...")
        self.download_manager = DownloadManager(
            self.http_client,
            self.lua_handler,
            self.db_manager,
            self.base_dir / 'downloads'
        )
        
        # Initialize clipboard monitor (desktop only)
        if not self.web_mode and not self.mobile_mode:
            print("Initializing clipboard monitor...")
            self.clipboard_monitor = ClipboardMonitor(self.on_clipboard_url_detected)
            self.clipboard_monitor.start()
        
        # Initialize tray icon (desktop only)
        if not self.web_mode and not self.mobile_mode:
            print("Initializing tray icon...")
            self.tray_icon = TrayIconManager(self.minimize_to_tray)
        
        print("Initialization complete!")
        
    def load_config(self):
        """Load application configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = {}
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self):
        """Get default configuration"""
        return {
            'general': {
                'one_instance_only': True,
                'check_updates': True,
                'language': 'en'
            },
            'downloads': {
                'max_concurrent': 3,
                'retry_count': 3,
                'save_format': 'cbz',
                'download_path': str(self.base_dir / 'downloads')
            },
            'network': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'timeout': 30,
                'proxy': None
            },
            'gui': {
                'theme': 'system',
                'compact_mode': False
            }
        }
    
    def save_config(self):
        """Save application configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def on_clipboard_url_detected(self, url):
        """Handle URL detected from clipboard"""
        # Check if it's a manga URL
        if self.module_loader and url:
            module = self.module_loader.find_module_for_url(url)
            if module:
                # Show dialog to add to downloads
                if self.page:
                    self.page.dialog = self.create_add_to_downloads_dialog(url, module)
                    self.page.dialog.open = True
                    self.page.update()
    
    def create_add_to_downloads_dialog(self, url, module):
        """Create dialog for adding manga to downloads"""
        dialog = ft.AlertDialog(
            title=ft.Text("Add to Downloads"),
            content=ft.Text(f"Detected manga URL from {module.name}:\n{url}"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog()),
                ft.TextButton("Add", on_click=lambda e: self.add_to_downloads(url, module))
            ]
        )
        return dialog
    
    def close_dialog(self):
        """Close current dialog"""
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.dialog = None
            self.page.update()
    
    def add_to_downloads(self, url, module):
        """Add manga to download queue"""
        self.close_dialog()
        # Add to download manager
        self.download_manager.add_manga(url, module)
        
        # Show notification
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Added {module.name} manga to downloads")
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def minimize_to_tray(self):
        """Minimize application to system tray"""
        if self.page and self.tray_icon:
            self.page.window.minimized = True
            self.page.update()
    
    def build_ui(self, page: ft.Page):
        """Build the main UI"""
        self.page = page
        
        # Configure page
        page.title = "Free Manga Downloader 2"
        page.theme_mode = ft.ThemeMode.SYSTEM
        page.padding = 0
        
        # Create main navigation view
        self.main_view = MainNavigationView(
            search_view=SearchView(self),
            downloads_view=DownloadsView(self),
            favorites_view=FavoritesView(self),
            settings_view=SettingsView(self)
        )
        
        # Add to page
        page.add(self.main_view.build())
        
        # Handle window close
        page.on_close = self.on_window_close
    
    def on_window_close(self, e):
        """Handle window close event"""
        # Stop background threads
        if self.clipboard_monitor:
            self.clipboard_monitor.stop()
        
        if self.download_manager:
            self.download_manager.stop()
        
        # Save config
        self.save_config()
        
        # Close database
        if self.db_manager:
            self.db_manager.close()
    
    def run(self):
        """Run the application"""
        # Initialize core components
        self.initialize()
        
        if self.web_mode:
            # Web mode - use ft.app with FLET_APP_WEB for pure web server accessible via browser
            print(f"Starting web server at http://{self.host}:{self.port}")
            ft.app(
                target=self.build_ui,
                assets_dir=str(self.base_dir / 'assets'),
                upload_dir=str(self.base_dir / 'uploads'),
                view=ft.AppView.FLET_APP_WEB,  # Pure web server mode accessible via browser
                host=self.host,
                port=self.port,
            )
        else:
            # Desktop/Mobile mode
            ft.app(
                target=self.build_ui,
                view=ft.AppView.FLET_APP if not self.mobile_mode else ft.AppView.WEB_BROWSER,
                assets_dir=str(self.base_dir / 'assets'),
                upload_dir=str(self.base_dir / 'uploads'),
            )


def main():
    """Main entry point"""
    app = FMD2Application()
    app.run()


if __name__ == '__main__':
    main()
