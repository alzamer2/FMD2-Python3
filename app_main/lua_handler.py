"""
FMD2 Python - Lua Handler Module
Provides Lua 5.4+ integration using lupa with isolated states
"""

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Callable

try:
    from lupa import LuaRuntime, as_attrgetter
except ImportError:
    print("Error: lupa library not installed. Run: pip install lupa")
    sys.exit(1)


class LuaHandler:
    """
    Lua handler for FMD2 Python
    Provides isolated Lua state with custom require wrapper
    """
    
    def __init__(self, lua_dir: Path, crypto=None, http_client=None, dofile: bool = False):
        # lua_dir should be the base directory containing modules/, templates/, utils/
        # If it ends with 'modules', go up one level
        lua_dir_path = Path(lua_dir)
        if lua_dir_path.name == 'modules':
            self.lua_dir = lua_dir_path.parent
        else:
            self.lua_dir = lua_dir_path
            
        self.crypto = crypto
        self.http_client = http_client
        self.dofile = dofile
        
        # Create isolated Lua runtime (Lua 5.4+)
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        
        # Setup Lua environment
        self._setup_lua_environment()
        
        # Register Python modules for Lua
        self._register_python_modules()
        
        # Cache for loaded modules
        self.loaded_modules = {}
        
    def _setup_lua_environment(self):
        """Setup Lua environment with custom functions"""
        lua = self.lua
        
        # Add utility functions including set_module_paths placeholder
        lua.execute('''
            -- Helper function to strip BOM
            function strip_bom(str)
                if str and str:byte(1, 3) == 239 then
                    return str:sub(4)
                end
                return str
            end
            
            -- Convert const to local for Lua 5.2+ compatibility
            function convert_const_to_local(code)
                return code:gsub("^%s*const%s+", "local ")
            end
            
            -- Placeholder for module paths (will be set later)
            local utils_path = nil
            local templates_path = nil
            
            function set_module_paths(utils, templates)
                utils_path = utils
                templates_path = templates
            end
        ''')
        
    def _register_python_modules(self):
        """Register Python modules accessible from Lua"""
        lua = self.lua
        
        # Register crypto module as fmd.crypto
        if self.crypto:
            fmd_table = lua.table()
            crypto_table = lua.table()
            
            crypto_table['base64_encode'] = self.crypto.base64_encode
            crypto_table['base64_decode'] = self.crypto.base64_decode
            crypto_table['md5'] = self.crypto.md5
            crypto_table['sha1'] = self.crypto.sha1
            crypto_table['sha256'] = self.crypto.sha256
            crypto_table['sha512'] = self.crypto.sha512
            crypto_table['hmac_sha256'] = self.crypto.hmac_sha256
            crypto_table['aes_cbc_encrypt'] = self.crypto.aes_cbc_encrypt
            crypto_table['aes_cbc_decrypt'] = self.crypto.aes_cbc_decrypt
            crypto_table['aes_ecb_encrypt'] = self.crypto.aes_ecb_encrypt
            crypto_table['aes_ecb_decrypt'] = self.crypto.aes_ecb_decrypt
            crypto_table['xor_cipher'] = self.crypto.xor_cipher
            
            fmd_table['crypto'] = crypto_table
            lua.globals()['fmd'] = fmd_table
        
        # Register HTTP client
        if self.http_client:
            lua.globals()['httpsend'] = self.http_client.create_lua_wrapper()
        
        # Set module paths first
        utils_path_val = str(self.lua_dir / 'utils')
        templates_path_val = str(self.lua_dir / 'templates')
        
        # Custom require implementation
        lua.execute(f'''
            local original_require = require
            local utils_path = "{utils_path_val}"
            local templates_path = "{templates_path_val}"
            
            function custom_require(module_name)
                -- Handle fmd.crypto specially
                if module_name == 'fmd.crypto' then
                    if fmd and fmd.crypto then
                        return fmd.crypto
                    end
                    error("fmd.crypto not available")
                end
                
                -- Check if already loaded
                if package.loaded[module_name] then
                    return package.loaded[module_name]
                end
                
                -- Handle utils.* modules
                if module_name:match("^utils%.") then
                    local file_path = utils_path .. "/" .. module_name:gsub("%.", "/") .. ".lua"
                    local file_handle = io.open(file_path, "r")
                    if file_handle then
                        local content = file_handle:read("*all")
                        file_handle:close()
                        content = strip_bom(content)
                        content = convert_const_to_local(content)
                        local chunk = load(content, module_name, "t")
                        if chunk then
                            package.loaded[module_name] = chunk()
                            return package.loaded[module_name]
                        end
                    end
                    error("Cannot load utils module: " .. module_name)
                end
                
                -- Handle templates.* modules
                if module_name:match("^templates%.") then
                    local file_path = templates_path .. "/" .. module_name:gsub("%.", "/") .. ".lua"
                    local file_handle = io.open(file_path, "r")
                    if file_handle then
                        local content = file_handle:read("*all")
                        file_handle:close()
                        content = strip_bom(content)
                        content = convert_const_to_local(content)
                        local chunk = load(content, module_name, "t")
                        if chunk then
                            package.loaded[module_name] = chunk()
                            return package.loaded[module_name]
                        end
                    end
                    error("Cannot load template module: " .. module_name)
                end
                
                -- Fallback to original require
                return original_require(module_name)
            end
            
            require = custom_require
        ''')
        
        # Pre-load all templates and utils into package.loaded
        self._preload_dependencies()
    
    def _preload_dependencies(self):
        """Pre-load all templates and utils into Lua's package.loaded table"""
        print("Pre-loading Lua dependencies...")
        
        # Pre-load utils
        utils_dir = self.lua_dir / 'utils'
        if utils_dir.exists():
            for lua_file in sorted(utils_dir.glob('*.lua')):
                try:
                    module_name = f"utils.{lua_file.stem}"
                    with open(lua_file, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    
                    content = self._strip_bom(content)
                    content = self._convert_const_to_local(content)
                    
                    # Load and execute the module using eval to get chunk
                    chunk = self.lua.eval(f"load({repr(content)}, {repr(module_name)}, 't')")
                    result = chunk()
                    
                    # Store in package.loaded using execute with ...
                    self.lua.execute(f"package.loaded['{module_name}'] = ...", result)
                    print(f"  ✓ Loaded {module_name}")
                except Exception as e:
                    print(f"  ✗ Failed to load {lua_file.name}: {e}")
        
        # Pre-load templates
        templates_dir = self.lua_dir / 'templates'
        if templates_dir.exists():
            for lua_file in sorted(templates_dir.glob('*.lua')):
                try:
                    module_name = f"templates.{lua_file.stem}"
                    with open(lua_file, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    
                    content = self._strip_bom(content)
                    content = self._convert_const_to_local(content)
                    
                    # Load and execute the module using eval to get chunk
                    chunk = self.lua.eval(f"load({repr(content)}, {repr(module_name)}, 't')")
                    result = chunk()
                    
                    # Store in package.loaded using execute with ...
                    self.lua.execute(f"package.loaded['{module_name}'] = ...", result)
                    print(f"  ✓ Loaded {module_name}")
                except Exception as e:
                    print(f"  ✗ Failed to load {lua_file.name}: {e}")
        
        print("Dependency pre-loading complete.")
    
    def execute(self, code: str, name: str = "<string>") -> Any:
        """Execute Lua code string"""
        # Strip BOM if present
        code = self._strip_bom(code)
        
        # Convert const to local for compatibility
        code = self._convert_const_to_local(code)
        
        try:
            # Use execute() for function definitions, eval() for expressions
            # Check if code contains function definitions
            if 'function ' in code or 'local function ' in code:
                self.lua.execute(code)
                return None  # Function definitions don't return a value
            else:
                chunk = self.lua.eval(code)
                return chunk
        except Exception as e:
            print(f"Lua execution error in {name}: {e}")
            raise
    
    def execute_file(self, filepath: str) -> Any:
        """Execute Lua file"""
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Lua file not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8-sig') as f:
            code = f.read()
        
        return self.execute(code, name=str(filepath))
    
    def load_module(self, module_name: str) -> Any:
        """Load a Lua module by name"""
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
        
        # Determine module type and path
        if module_name.startswith('utils.'):
            module_path = self.lua_dir / 'utils' / f"{module_name.replace('.', '/')}.lua"
        elif module_name.startswith('templates.'):
            module_path = self.lua_dir / 'templates' / f"{module_name.replace('.', '/')}.lua"
        else:
            module_path = self.lua_dir / 'modules' / f"{module_name}.lua"
        
        if not module_path.exists():
            raise FileNotFoundError(f"Module not found: {module_path}")
        
        # Load the module using execute_file which handles BOM and const conversion
        result = self.execute_file(str(module_path))
        self.loaded_modules[module_name] = result
        return result
    
    def load_module_from_file(self, filepath: str) -> Any:
        """Load a Lua module directly from file path"""
        path = Path(filepath)
        module_name = path.stem
        
        if not path.exists():
            raise FileNotFoundError(f"Module file not found: {filepath}")
        
        # Load the module
        result = self.execute_file(str(path))
        self.loaded_modules[module_name] = result
        return result
    
    def _strip_bom(self, code: str) -> str:
        """Strip UTF-8 BOM from code"""
        if code and len(code) >= 3:
            if ord(code[0]) == 0xEF and ord(code[1]) == 0xBB and ord(code[2]) == 0xBF:
                return code[3:]
        return code
    
    def _convert_const_to_local(self, code: str) -> str:
        """Convert const declarations to local for Lua 5.2+ compatibility"""
        # Simple regex replacement for const at start of lines
        code = re.sub(r'^(\s*)const\s+', r'\1local ', code, flags=re.MULTILINE)
        
        # Handle const in for loops: "for const i = ..." -> "for i = ..."
        code = re.sub(r'for\s+const\s+', 'for ', code)
        
        # Fix loop variable modification issue in Lua 5.2+
        # Pattern: for i = X, Y do ... i = i + 1 ... end
        # We need to wrap the loop body in a function or use a different approach
        # For now, we'll convert problematic patterns where loop var is modified
        
        # Handle pattern: for i = 0, COUNT - 1 do ... i = i + 1 ... end
        # Replace with: for i_new = 0, COUNT - 1 do i = i_new; ... end
        def fix_loop_var_modification(match):
            loop_start = match.group(0)
            var_name = match.group(1)
            return loop_start  # Keep as is, we'll handle differently
        
        # More aggressive: find for loops and replace modifications inside
        # This is complex, so let's use a simpler approach:
        # Just remove the problematic "i = i + 1" lines since they're redundant in numeric for loops
        code = re.sub(r'^(\s*)(\w+)\s*=\s*\2\s*\+\s*1\s*$', r'\1-- \2 = \2 + 1 (removed, redundant in numeric for)', code, flags=re.MULTILINE)
        
        return code
    
    def create_table(self, data: Dict[str, Any] = None) -> Any:
        """Create a Lua table from Python dict"""
        if data is None:
            return self.lua.table()
        return self.lua.table_from(data)
    
    def get_globals(self) -> Any:
        """Get Lua globals table"""
        return self.lua.globals
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a Python function in Lua globals"""
        self.lua.globals[name] = func
    
    def register_module(self, name: str, module_dict: Dict[str, Any]) -> None:
        """Register a Python module in Lua globals"""
        self.lua.globals[name] = self.lua.table_from(module_dict)
