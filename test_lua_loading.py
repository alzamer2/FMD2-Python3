#!/usr/bin/env python3
"""
Test script to verify Lua module loading with dependency pre-loading
"""

import sys
from pathlib import Path

# Add app_main to path
sys.path.insert(0, str(Path(__file__).parent))

from app_main.lua_handler import LuaHandler
from app_main.fmd_crypto import FMDCrypto
from app_main.http_client import HTTPClient

def test_lua_loading():
    """Test loading all Lua modules with pre-loaded dependencies"""
    
    lua_dir = Path(__file__).parent / 'lua'
    
    print("=" * 60)
    print("FMD2 Python - Lua Module Loading Test")
    print("=" * 60)
    
    # Initialize components
    crypto = FMDCrypto()
    http_client = HTTPClient()
    
    # Create Lua handler (this will pre-load dependencies)
    print("\nInitializing Lua handler with dependency pre-loading...")
    lua_handler = LuaHandler(lua_dir=lua_dir, crypto=crypto, http_client=http_client)
    
    # Count total modules
    modules_dir = lua_dir / 'modules'
    lua_files = list(modules_dir.glob('*.lua'))
    total_modules = len(lua_files)
    
    print(f"\nFound {total_modules} Lua module files to test")
    print("-" * 60)
    
    # Test loading each module
    success_count = 0
    error_count = 0
    errors = []
    
    for i, lua_file in enumerate(lua_files, 1):
        try:
            with open(lua_file, 'r', encoding='utf-8-sig') as f:
                code = f.read()
            
            # Strip BOM and convert const
            code = lua_handler._strip_bom(code)
            code = lua_handler._convert_const_to_local(code)
            
            # Try to execute
            if 'function ' in code or 'local function ' in code:
                lua_handler.execute(code, name=lua_file.name)
            else:
                lua_handler.execute(code, name=lua_file.name)
            
            success_count += 1
            status = "✓"
        except Exception as e:
            error_count += 1
            status = "✗"
            errors.append((lua_file.name, str(e)))
        
        # Progress indicator every 100 modules
        if i % 100 == 0:
            print(f"Processed {i}/{total_modules} modules...")
    
    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total modules:     {total_modules}")
    print(f"Successfully loaded: {success_count} ({100*success_count/total_modules:.1f}%)")
    print(f"Failed to load:    {error_count} ({100*error_count/total_modules:.1f}%)")
    
    if errors:
        print("\n" + "-" * 60)
        print("ERRORS (first 20):")
        print("-" * 60)
        for filename, error in errors[:20]:
            print(f"  {filename}: {error[:100]}")
        
        if len(errors) > 20:
            print(f"\n  ... and {len(errors) - 20} more errors")
    
    print("\n" + "=" * 60)
    
    # Check if we reached the 90% target
    success_rate = 100 * success_count / total_modules
    if success_rate >= 90:
        print("✓ SUCCESS: Achieved >90% module loading target!")
    else:
        print(f"✗ NEEDS IMPROVEMENT: {success_rate:.1f}% < 90% target")
    
    return success_count, error_count, errors

if __name__ == '__main__':
    test_lua_loading()
