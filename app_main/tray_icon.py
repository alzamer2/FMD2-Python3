"""
FMD2 Python - System Tray Icon Manager
Provides system tray integration with minimize-to-tray functionality
"""

import threading
from typing import Callable, Optional


class TrayIconManager:
    """
    Manages system tray icon for FMD2
    Uses pystray for cross-platform tray support
    """
    
    def __init__(self, on_minimize: Callable = None, on_restore: Callable = None):
        self.on_minimize = on_minimize
        self.on_restore = on_restore
        self.tray_icon = None
        self.thread = None
    
    def start(self):
        """Start the tray icon in a background thread"""
        try:
            import pystray
            from PIL import Image
            
            # Create menu items
            menu_items = [
                pystray.MenuItem("Show/Restore", self._on_show, default=True),
                pystray.MenuItem("Minimize to Tray", self._on_minimize),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", self._on_quit),
            ]
            
            # Create a simple icon (1x1 pixel placeholder)
            # In production, use actual icon file
            icon_image = Image.new('RGB', (64, 64), color='blue')
            
            self.tray_icon = pystray.Icon(
                name="FMD2",
                icon=icon_image,
                title="Free Manga Downloader 2",
                menu=pystray.Menu(*menu_items)
            )
            
            # Run in separate thread
            self.thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.thread.start()
            
        except ImportError:
            print("pystray not available, tray icon disabled")
        except Exception as e:
            print(f"Error creating tray icon: {e}")
    
    def _on_show(self, icon=None, item=None):
        """Handle show/restore action"""
        if self.on_restore:
            self.on_restore()
    
    def _on_minimize(self, icon=None, item=None):
        """Handle minimize to tray action"""
        if self.on_minimize:
            self.on_minimize()
    
    def _on_quit(self, icon=None, item=None):
        """Handle quit action"""
        if self.tray_icon:
            self.tray_icon.stop()
        
        import sys
        sys.exit(0)
    
    def stop(self):
        """Stop the tray icon"""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
    
    def show_notification(self, title: str, message: str):
        """Show a notification from tray"""
        if self.tray_icon:
            try:
                self.tray_icon.notify(message=message, title=title)
            except Exception:
                pass
