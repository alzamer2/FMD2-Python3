"""
FMD2 Python - Module Loader
Loads and manages 600+ Lua scraper modules
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any


class MangaModule:
    """Represents a loaded manga scraper module"""
    
    def __init__(self, name: str, lua_code: str, lua_handler):
        self.name = name
        self.lua_code = lua_code
        self.lua_handler = lua_handler
        self.module_data = None
        self.enabled = True
        
        # Module metadata (extracted from Lua)
        self.id = None
        self.site_url = None
        self.language = None
        self.categories = []
        
        self._parse_metadata()
    
    def _parse_metadata(self):
        """Parse module metadata from Lua code"""
        # Extract module name
        match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', self.lua_code)
        if match:
            self.name = match.group(1)
        
        # Extract ID
        match = re.search(r'id\s*=\s*["\']([^"\']+)["\']', self.lua_code)
        if match:
            self.id = match.group(1)
        
        # Extract site URL
        match = re.search(r'siteUrl\s*=\s*["\']([^"\']+)["\']', self.lua_code)
        if match:
            self.site_url = match.group(1)
        
        # Extract language
        match = re.search(r'lang\s*=\s*["\']([^"\']+)["\']', self.lua_code)
        if match:
            self.language = match.group(1)
        
        # Extract categories
        match = re.search(r'categories\s*=\s*\{([^}]+)\}', self.lua_code)
        if match:
            cats = match.group(1)
            self.categories = re.findall(r'["\']([^"\']+)["\']', cats)
    
    def load(self) -> bool:
        """Load the module into Lua state"""
        try:
            result = self.lua_handler.execute(self.lua_code, name=f"module_{self.name}")
            self.module_data = result
            return True
        except Exception as e:
            print(f"Error loading module {self.name}: {e}")
            return False
    
    def search(self, query: str) -> List[Dict]:
        """Search for manga using this module"""
        if not self.module_data:
            self.load()
        
        # Call module's search function if it exists
        lua_globals = self.lua_handler.get_globals()
        if hasattr(lua_globals, 'GetDirectoryPageNumber'):
            # FMD2 module interface
            pass
        
        # TODO: Implement search based on FMD2 module interface
        return []
    
    def get_manga_info(self, url: str) -> Dict:
        """Get manga information from URL"""
        if not self.module_data:
            self.load()
        
        # TODO: Implement based on FMD2 module interface
        return {}
    
    def get_chapter_pages(self, url: str) -> List[str]:
        """Get chapter page URLs"""
        if not self.module_data:
            self.load()
        
        # TODO: Implement based on FMD2 module interface
        return []


class ModuleLoader:
    """
    Loads and manages all Lua scraper modules
    """
    
    def __init__(self, lua_handler):
        self.lua_handler = lua_handler
        self.modules_dir = lua_handler.lua_dir / 'modules'
        self.templates_dir = lua_handler.lua_dir / 'templates'
        self.loaded_modules: List[MangaModule] = []
        self.modules_by_id: Dict[str, MangaModule] = {}
        self.modules_by_name: Dict[str, MangaModule] = {}
        self.templates: Dict[str, Any] = {}
        
    def load_all_modules(self) -> List[MangaModule]:
        """Load all available modules"""
        print("Loading modules from:", self.modules_dir)
        
        # Load templates first
        self._load_templates()
        
        # Load all module files
        if not self.modules_dir.exists():
            print(f"Modules directory not found: {self.modules_dir}")
            return []
        
        lua_files = list(self.modules_dir.glob('*.lua'))
        print(f"Found {len(lua_files)} Lua module files")
        
        success_count = 0
        error_count = 0
        
        for lua_file in lua_files:
            try:
                module = self.load_module_from_file(lua_file)
                if module:
                    self.loaded_modules.append(module)
                    if module.id:
                        self.modules_by_id[module.id] = module
                    self.modules_by_name[module.name.lower()] = module
                    success_count += 1
            except Exception as e:
                print(f"Error loading {lua_file.name}: {e}")
                error_count += 1
        
        print(f"Successfully loaded {success_count} modules ({error_count} errors)")
        return self.loaded_modules
    
    def load_module_from_file(self, filepath: Path) -> Optional[MangaModule]:
        """Load a single module from file"""
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                lua_code = f.read()
            
            module = MangaModule(
                name=filepath.stem,
                lua_code=lua_code,
                lua_handler=self.lua_handler
            )
            
            # Try to load the module
            if module.load():
                return module
            else:
                return None
                
        except Exception as e:
            print(f"Error reading module file {filepath}: {e}")
            return None
    
    def _load_templates(self):
        """Load template modules"""
        if not self.templates_dir.exists():
            return
        
        for lua_file in self.templates_dir.glob('*.lua'):
            try:
                with open(lua_file, 'r', encoding='utf-8-sig') as f:
                    lua_code = f.read()
                
                # Execute template code
                result = self.lua_handler.execute(lua_code, name=f"template_{lua_file.stem}")
                self.templates[lua_file.stem] = result
                
            except Exception as e:
                print(f"Error loading template {lua_file.name}: {e}")
    
    def find_module_for_url(self, url: str) -> Optional[MangaModule]:
        """Find the appropriate module for a given URL"""
        for module in self.loaded_modules:
            if module.site_url and module.site_url in url:
                return module
            
            # Check domain matching
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                if module.site_url:
                    module_domain = urlparse(module.site_url).netloc.lower()
                    if module_domain in domain or domain in module_domain:
                        return module
            except:
                pass
        
        return None
    
    def get_module_by_id(self, module_id: str) -> Optional[MangaModule]:
        """Get module by ID"""
        return self.modules_by_id.get(module_id)
    
    def get_module_by_name(self, name: str) -> Optional[MangaModule]:
        """Get module by name"""
        return self.modules_by_name.get(name.lower())
    
    def search_modules(self, query: str) -> List[MangaModule]:
        """Search modules by name or category"""
        query = query.lower()
        results = []
        
        for module in self.loaded_modules:
            if not module.enabled:
                continue
            
            # Search in name
            if query in module.name.lower():
                results.append(module)
                continue
            
            # Search in categories
            for cat in module.categories:
                if query in cat.lower():
                    results.append(module)
                    break
        
        return results
    
    def get_enabled_modules(self) -> List[MangaModule]:
        """Get all enabled modules"""
        return [m for m in self.loaded_modules if m.enabled]
    
    def enable_module(self, module_id: str) -> bool:
        """Enable a module"""
        module = self.get_module_by_id(module_id)
        if module:
            module.enabled = True
            return True
        return False
    
    def disable_module(self, module_id: str) -> bool:
        """Disable a module"""
        module = self.get_module_by_id(module_id)
        if module:
            module.enabled = False
            return True
        return False
    
    def reload_module(self, module_id: str) -> bool:
        """Reload a module from file"""
        module = self.get_module_by_id(module_id)
        if module:
            # Find the file
            module_file = self.modules_dir / f"{module_id}.lua"
            if module_file.exists():
                new_module = self.load_module_from_file(module_file)
                if new_module:
                    # Replace old module
                    idx = self.loaded_modules.index(module)
                    self.loaded_modules[idx] = new_module
                    self.modules_by_id[new_module.id] = new_module
                    self.modules_by_name[new_module.name.lower()] = new_module
                    return True
        return False
