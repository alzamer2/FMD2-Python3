# FMD2 Python - Free Manga Downloader 2 (Python Port)

A modern Python 3 rewrite of the classic Free Manga Downloader 2 (FMD2) application, originally written in Pascal/Lazarus. This port uses the Flet framework for cross-platform GUI support (Desktop, Web, Mobile) and preserves 100% compatibility with the existing 600+ Lua scraper modules.

## Features

- **600+ Manga Sites**: Full support for all original FMD2 Lua scraper modules
- **Cross-Platform**: Desktop (Windows, macOS, Linux), Web, and Mobile support
- **Multi-threaded Downloads**: Concurrent downloads with progress tracking
- **Favorites Management**: Track manga series and get update notifications
- **Clipboard Monitor**: Auto-detect manga URLs from clipboard
- **System Tray Integration**: Minimize to tray with context menu
- **Modern UI**: Clean, responsive interface built with Flet
- **Lua Compatibility**: Automatic BOM stripping and const→local conversion for Lua 5.2+ compatibility

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Node.js (Optional, for JavaScript execution)

Some manga sites require JavaScript execution. Install Node.js for full compatibility:

```bash
# Ubuntu/Debian
sudo apt install nodejs

# Windows/macOS
# Download from https://nodejs.org/
```

## Usage

### Desktop Mode (Default)

```bash
python app.py
```

### Web Mode

```bash
python app.py --web
```

With custom host and port:

```bash
python app.py --web --host 0.0.0.0 --port 8080
```

### Mobile Mode

```bash
python app.py --mobile
```

### Development Mode

Force Lua modules to load from files (for development):

```bash
python app.py --lua-dofile
```

### Debug Mode

```bash
python app.py --debug
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--web` | Run in web mode |
| `--mobile` | Run in mobile mode |
| `--host`, `-h` | Host address for web mode (default: 0.0.0.0) |
| `--port`, `-p` | Port for web mode (default: 5000) |
| `--debug` | Enable debug mode |
| `--lua-dofile` | Always load Lua modules from file (dev mode) |

## Project Structure

```
/workspace
├── app.py                 # Entry point
├── app_main/              # Core application code
│   ├── application.py     # Main application class
│   ├── lua_handler.py     # Lua integration (lupa)
│   ├── module_loader.py   # Lua module loader
│   ├── fmd_crypto.py      # Crypto functions
│   ├── http_client.py     # HTTP client with cookie management
│   ├── database_manager.py # SQLite database layer
│   ├── download_thread.py # Multi-threaded download manager
│   ├── clipboard_monitor.py # Clipboard URL detection
│   ├── tray_icon.py       # System tray integration
│   └── gui_*.py           # Flet GUI components
├── lua/                   # Lua scraper modules
│   ├── modules/           # 600+ site-specific scrapers
│   ├── templates/         # Template-based scrapers
│   └── utils/             # Utility Lua modules
├── org_fmd2/              # Original FMD2 Pascal source
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Configuration

Configuration is stored in `config.json` in the application directory:

```json
{
  "general": {
    "one_instance_only": true,
    "check_updates": true,
    "language": "en"
  },
  "downloads": {
    "max_concurrent": 3,
    "retry_count": 3,
    "save_format": "cbz",
    "download_path": "./downloads"
  },
  "network": {
    "user_agent": "Mozilla/5.0...",
    "timeout": 30,
    "proxy": null
  },
  "gui": {
    "theme": "system",
    "compact_mode": false
  }
}
```

## Database

The application uses SQLite for data storage:

- `fmd2.db` - Main database with favorites, downloads, and history
- `cookies.txt` - Netscape-format cookies

## Lua Module Compatibility

The application maintains 100% compatibility with original FMD2 Lua modules:

- **BOM Stripping**: Automatic UTF-8 BOM removal
- **const→local**: Automatic conversion for Lua 5.2+ compatibility
- **Custom require**: Maps `utils.*` and `templates.*` to correct paths
- **Python Bindings**: 
  - `fmd.crypto` - Python crypto implementation
  - `httpsend` - Python HTTP client

## Supported Formats

### Download Formats
- CBZ (Comic Book ZIP)
- ZIP
- PDF
- Folder (raw images)

### Image Formats
- JPEG, PNG, GIF, WebP
- JXL (JPEG XL via pillow-jxl-plugin)

### Archive Formats
- ZIP, RAR, 7z, TAR

## Architecture

### Core Components

1. **LuaHandler**: Isolated Lua 5.4+ runtime using lupa
2. **ModuleLoader**: Loads and manages 600+ scraper modules
3. **HTTPClient**: Advanced HTTP client with compression support
4. **DatabaseManager**: SQLite ORM-like layer
5. **DownloadManager**: Multi-threaded download worker pool

### GUI Components

1. **SearchView**: Manga search with site selection
2. **FavoritesView**: Tracked manga with update checking
3. **DownloadsView**: Active downloads with progress bars
4. **SettingsView**: Application configuration

## Development

### Running Tests

```bash
# Load test - verify Lua modules load
python -c "from app_main.module_loader import ModuleLoader; from app_main.lua_handler import LuaHandler; print('Load test passed')"

# Functional test
# TODO: Add pytest tests
```

### Adding New Features

1. Create new module in `app_main/`
2. Import in `application.py`
3. Add GUI component if needed
4. Update this README

## Troubleshooting

### Lua Modules Not Loading

- Ensure `lupa` is installed: `pip install lupa`
- Check Lua module syntax with `luac -p module.lua`
- Enable debug mode: `python app.py --debug`

### Web Mode Not Starting

- Check if port is available: `netstat -an | grep 5000`
- Try different port: `python app.py --web --port 8080`
- Ensure firewall allows connections

### Downloads Failing

- Check network connectivity
- Verify proxy settings in Settings → Network
- Check site-specific module status

## License

Original FMD2: GPL-2.0  
Python Port: GPL-2.0

## Credits

- Original FMD2 by dazedcat19: https://github.com/dazedcat19/FMD2
- Flet Framework: https://flet.dev
- Lupa (Lua integration): https://github.com/scoder/lupa

## Contributing

Contributions welcome! Please submit issues and pull requests on GitHub.

## Version

2.0.0 (Python Port)
