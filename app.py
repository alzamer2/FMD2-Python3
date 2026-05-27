"""
FMD2 Python - Free Manga Downloader 2 (Python Port)
Entry Point - Supports Desktop, Web, and Mobile modes

Usage:
    python app.py                    # Desktop mode (default)
    python app.py --web              # Web mode
    python app.py --web --host 0.0.0.0 --port 8080  # Web mode with custom host/port
"""

import sys
import argparse
import os

# Add app_main to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app_main'))


def parse_args():
    parser = argparse.ArgumentParser(description='Free Manga Downloader 2 (Python Port)')
    
    # Mode selection
    parser.add_argument('--web', action='store_true', help='Run in web mode')
    parser.add_argument('--mobile', action='store_true', help='Run in mobile mode')
    
    # Web server options
    parser.add_argument('--ip', type=str, default='0.0.0.0', 
                        help='IP address for web mode (default: 0.0.0.0)')
    parser.add_argument('--port', '-p', type=int, default=5000,
                        help='Port for web mode (default: 5000)')
    
    # Debug options
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--lua-dofile', action='store_true', 
                        help='Always load Lua modules from file (dev mode)')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Set environment variables for Lua loading
    if args.lua_dofile:
        os.environ['FMD_LUA_DOFILE'] = '1'
    
    # Import the main application
    from app_main.application import FMD2Application
    
    # Create and run the application
    app = FMD2Application(
        web_mode=args.web,
        mobile_mode=args.mobile,
        host=args.ip,
        port=args.port,
        debug=args.debug
    )
    
    # Run the application
    app.run()


if __name__ == '__main__':
    main()
