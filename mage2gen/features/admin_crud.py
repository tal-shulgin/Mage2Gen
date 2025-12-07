from . import Feature
from ..snippets.model import ModelSnippet
from ..snippets.controller import ControllerSnippet
from ..utils import upperfirst, lowerfirst

class AdminCrudFeature(Feature):
    description = "Generates a full Admin CRUD (Grid + Form) with working Save/Delete logic."

    def add(self, name, fields="", menu_parent="Magento_Backend::content"):
        entity_name = upperfirst(name)
        package = self._module.package
        module = self._module.name
        
        # Prepare Context Data for Logic Injection
        id_field = f"{name.lower()}_id"
        table_name = f"{package.lower()}_{module.lower()}_{name.lower()}"
        
        entity_context = {
            'model_name': entity_name,
            'model_namespace': f"{package}\\{module}\\Model",
            'repository_interface': f"{package}\\{module}\\Api\\{entity_name}RepositoryInterface",
            'id_field': id_field,
            'table_name': table_name
        }

        # 1. Generate Model
        print(f"  [Feature] Generating Model: {entity_name}...")
        model_snippet = ModelSnippet(self._module)
        model_snippet.add(
            name=entity_name, 
            fields=fields, 
            admin_grid=True, 
            api=True
        )

        # 2. Generate Logic-Injected Controllers
        print(f"  [Feature] Generating Smart Controllers...")
        controller = ControllerSnippet(self._module)
        
        # Index (Grid) - Still generic for now
        controller.add(
            frontname=None, 
            section=entity_name.lower(),
            action='index',
            adminhtml=True
        )
        
        # Edit (Form) - Generic (wraps UI Component)
        controller.add(
            frontname=None,
            section=entity_name.lower(),
            action='edit',
            adminhtml=True
        )
        
        # Save (Logic Injected)
        controller.add(
            frontname=None,
            section=entity_name.lower(),
            action='save',
            adminhtml=True,
            entity_context=entity_context
        )
        
        # Delete (Logic Injected)
        controller.add(
            frontname=None,
            section=entity_name.lower(),
            action='delete',
            adminhtml=True,
            entity_context=entity_context
        )

        print(f"  [Feature] Admin CRUD for {entity_name} generated successfully.")