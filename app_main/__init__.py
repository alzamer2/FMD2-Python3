"""
FMD2 Python - Free Manga Downloader 2 (Python Port)
Core application package
"""

from app_main.application import FMD2Application
from app_main.lua_handler import LuaHandler
from app_main.module_loader import ModuleLoader, MangaModule
from app_main.fmd_crypto import FMDCrypto, get_crypto
from app_main.http_client import HTTPClient, CookieManager
from app_main.database_manager import DatabaseManager
from app_main.download_thread import DownloadManager, DownloadTask, DownloadStatus

__version__ = "2.0.0"
__author__ = "FMD2 Python Contributors"

__all__ = [
    'FMD2Application',
    'LuaHandler',
    'ModuleLoader',
    'MangaModule',
    'FMDCrypto',
    'get_crypto',
    'HTTPClient',
    'CookieManager',
    'DatabaseManager',
    'DownloadManager',
    'DownloadTask',
    'DownloadStatus',
]
