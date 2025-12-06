from . import Feature
from ..snippets.model import ModelSnippet
from ..snippets.controller import ControllerSnippet
from ..utils import upperfirst

class AdminCrudFeature(Feature):
    description = "Generates a full Admin CRUD (Grid + Form) including Model, Controllers, and Menu."

    def add(self, name, fields="", menu_parent="Magento_Backend::content"):
        entity_name = upperfirst(name)
        
        # 1. Generate Model (Database, Repository, Interfaces)
        # We enable 'admin_grid' so the ModelSnippet generates the base UI Component XML
        print(f"  [Feature] Generating Model: {entity_name}...")
        model_snippet = ModelSnippet(self._module)
        model_snippet.add(
            name=entity_name, 
            fields=fields, 
            admin_grid=True, # This triggers basic listing.xml generation in ModelSnippet
            api=True
        )

        # 2. Generate Controllers (Index, Edit, Save, Delete, New)
        # Note: We are using the standard ControllerSnippet we refactored earlier
        print(f"  [Feature] Generating Admin Controllers...")
        controller = ControllerSnippet(self._module)
        
        # Index (Grid)
        controller.add(
            frontname=None, # Auto-resolve
            section=entity_name.lower(),
            action='index',
            adminhtml=True
        )
        
        # Edit (Form)
        controller.add(
            frontname=None,
            section=entity_name.lower(),
            action='edit',
            adminhtml=True
        )
        
        # Save
        controller.add(
            frontname=None,
            section=entity_name.lower(),
            action='save',
            adminhtml=True
        )
        
        # Delete
        controller.add(
            frontname=None,
            section=entity_name.lower(),
            action='delete',
            adminhtml=True
        )

        print(f"  [Feature] Admin CRUD for {entity_name} generated successfully.")
