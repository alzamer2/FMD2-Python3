"""
FMD2 Python - Search View
Manga search with site selection and results grid
"""

import flet as ft
from typing import List, Dict, Optional


class SearchView:
    """
    Search view for finding manga across 600+ sites
    """
    
    def __init__(self, app):
        self.app = app
        self.search_field = None
        self.site_dropdown = None
        self.results_grid = None
        self.loading_indicator = None
    
    def build(self) -> ft.Column:
        """Build the search UI"""
        # Site selector dropdown
        self.site_dropdown = ft.Dropdown(
            label="Select Site",
            width=300,
            options=[],
            on_change=self._on_site_change
        )
        
        # Populate sites from loaded modules
        self._populate_sites()
        
        # Search field
        self.search_field = ft.TextField(
            label="Search Manga",
            hint_text="Enter manga title...",
            expand=True,
            on_submit=self._on_search,
            suffix_icon=ft.icons.SEARCH,
        )
        
        # Search button
        search_button = ft.ElevatedButton(
            "Search",
            icon=ft.icons.SEARCH,
            on_click=self._on_search
        )
        
        # Loading indicator
        self.loading_indicator = ft.ProgressRing(visible=False)
        
        # Results grid
        self.results_grid = ft.GridView(
            expand=True,
            runs_count=5,
            max_extent=200,
            spacing=10,
            run_spacing=10,
        )
        
        # Search bar row
        search_bar = ft.Row(
            controls=[
                self.site_dropdown,
                self.search_field,
                search_button,
                self.loading_indicator,
            ],
            alignment=ft.MainAxisAlignment.START,
        )
        
        return ft.Column(
            controls=[
                search_bar,
                ft.Container(
                    expand=True,
                    content=self.results_grid,
                ),
            ],
            expand=True,
        )
    
    def _populate_sites(self):
        """Populate site dropdown with loaded modules"""
        if not self.app or not self.app.module_loader:
            return
        
        modules = self.app.module_loader.get_enabled_modules()
        
        # Group by language
        sites_by_lang = {}
        for module in modules:
            lang = module.language or 'en'
            if lang not in sites_by_lang:
                sites_by_lang[lang] = []
            sites_by_lang[lang].append(module)
        
        # Create dropdown options
        options = []
        for lang in sorted(sites_by_lang.keys()):
            options.append(ft.dropdown.Option(text=f"--- {lang.upper()} ---", disabled=True))
            for module in sorted(sites_by_lang[lang], key=lambda m: m.name):
                options.append(
                    ft.dropdown.Option(
                        key=module.id or module.name,
                        text=f"{module.name}"
                    )
                )
        
        self.site_dropdown.options = options
    
    def _on_site_change(self, e):
        """Handle site selection change"""
        pass
    
    def _on_search(self, e):
        """Handle search action"""
        query = self.search_field.value.strip()
        site_key = self.site_dropdown.value
        
        if not query:
            return
        
        # Show loading
        self.loading_indicator.visible = True
        self.search_field.page.update()
        
        # Perform search (async)
        import threading
        threading.Thread(target=self._perform_search, args=(query, site_key), daemon=True).start()
    
    def _perform_search(self, query: str, site_key: str):
        """Perform search in background thread"""
        try:
            # Find selected module
            module = None
            if site_key:
                module = self.app.module_loader.get_module_by_id(site_key)
                if not module:
                    module = self.app.module_loader.get_module_by_name(site_key)
            
            if module:
                # Search using specific module
                results = module.search(query)
            else:
                # Search all modules
                results = []
                for mod in self.app.module_loader.get_enabled_modules():
                    mod_results = mod.search(query)
                    results.extend(mod_results)
            
            # Update UI with results
            self._update_results(results)
            
        except Exception as e:
            print(f"Search error: {e}")
        finally:
            # Hide loading
            self.loading_indicator.visible = False
            if self.search_field.page:
                self.search_field.page.update()
    
    def _update_results(self, results: List[Dict]):
        """Update results grid"""
        # Clear existing results
        self.results_grid.controls.clear()
        
        for result in results:
            # Create manga card
            card = self._create_manga_card(result)
            self.results_grid.controls.append(card)
        
        if self.search_field.page:
            self.search_field.page.update()
    
    def _create_manga_card(self, manga_info: Dict) -> ft.Card:
        """Create a manga result card"""
        title = manga_info.get('title', 'Unknown')
        cover_url = manga_info.get('cover_url', '')
        author = manga_info.get('author', '')
        
        # Cover image or placeholder
        if cover_url:
            cover_image = ft.Image(
                src=cover_url,
                fit=ft.ImageFit.COVER,
                width=150,
                height=200,
                error_content=ft.Container(
                    width=150,
                    height=200,
                    bgcolor=ft.colors.GREY_300,
                    content=ft.Icon(ft.icons.IMAGE_NOT_SUPPORTED, size=50)
                )
            )
        else:
            cover_image = ft.Container(
                width=150,
                height=200,
                bgcolor=ft.colors.GREY_300,
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.MENU_BOOK, size=50),
                        ft.Text("No Cover", size=12),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        cover_image,
                        ft.Text(title, size=14, weight=ft.FontWeight.BOLD, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(author, size=12, color=ft.colors.GREY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Row(
                            controls=[
                                ft.TextButton("Info", icon=ft.icons.INFO_OUTLINE),
                                ft.TextButton("Download", icon=ft.icons.DOWNLOAD),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        ),
                    ],
                    spacing=5,
                ),
                padding=10,
            ),
        )
    
    def focus_search(self):
        """Focus the search field"""
        if self.search_field:
            self.search_field.focus()
