"""
FMD2 Python - Clipboard Monitor
Background thread that watches clipboard for manga URLs
"""

import threading
import time
import re
from typing import Callable, Optional


class ClipboardMonitor(threading.Thread):
    """
    Monitors system clipboard for manga URLs
    """
    
    # Common manga site URL patterns
    MANGA_URL_PATTERNS = [
        r'https?://(?:www\.)?mangadex\.org/.*',
        r'https?://(?:www\.)?asurascans\.com/.*',
        r'https?://(?:www\.)?flamescans\.org/.*',
        r'https?://(?:www\.)?reaperscans\.com/.*',
        r'https?://(?:www\.)?luminousscans\.com/.*',
        r'https?://(?:www\.)?manganato\.com/.*',
        r'https?://(?:www\.)?mangakakalot\.com/.*',
        r'https?://(?:www\.)?readmanga\.today/.*',
        r'https?://(?:www\.)?batoto\.com/.*',
    ]
    
    def __init__(self, on_url_detected: Callable[[str], None], 
                 check_interval: float = 1.0):
        super().__init__(daemon=True)
        self.on_url_detected = on_url_detected
        self.check_interval = check_interval
        self.running = False
        self.last_clipboard_content = None
    
    def run(self):
        """Main monitoring loop"""
        self.running = True
        
        while self.running:
            try:
                current_content = self.get_clipboard_text()
                
                if current_content and current_content != self.last_clipboard_content:
                    if self.is_manga_url(current_content):
                        self.on_url_detected(current_content)
                    
                    self.last_clipboard_content = current_content
                    
            except Exception as e:
                # Silently ignore clipboard errors
                pass
            
            time.sleep(self.check_interval)
    
    def get_clipboard_text(self) -> Optional[str]:
        """Get current clipboard text"""
        try:
            # Try different clipboard methods based on platform
            import subprocess
            import sys
            
            if sys.platform == 'win32':
                # Windows
                result = subprocess.run(['clip.exe'], capture_output=True, text=True)
                return result.stdout.strip() if result.returncode == 0 else None
                
            elif sys.platform == 'darwin':
                # macOS
                result = subprocess.run(['pbpaste'], capture_output=True, text=True)
                return result.stdout.strip() if result.returncode == 0 else None
                
            else:
                # Linux - try xclip or xsel
                try:
                    result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'],
                                          capture_output=True, text=True)
                    return result.stdout.strip() if result.returncode == 0 else None
                except FileNotFoundError:
                    try:
                        result = subprocess.run(['xsel', '--clipboard', '--output'],
                                              capture_output=True, text=True)
                        return result.stdout.strip() if result.returncode == 0 else None
                    except FileNotFoundError:
                        pass
            
            return None
            
        except Exception:
            return None
    
    def is_manga_url(self, text: str) -> bool:
        """Check if text is a manga URL"""
        if not text or len(text) > 500:
            return False
        
        # Must start with http
        if not text.startswith('http'):
            return False
        
        # Check against known patterns
        for pattern in self.MANGA_URL_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        # Generic check for manga-related domains
        manga_keywords = ['manga', 'comic', 'manhua', 'manhwa', 'toon']
        text_lower = text.lower()
        
        for keyword in manga_keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
