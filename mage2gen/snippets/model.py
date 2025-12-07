import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst, lowerfirst, merge_xml_files
from ..schema import Table
from ..types import get_php_type, get_php_doc_type

class ModelSnippet(Snippet):
    snippet_label = 'Model (CRUD)'
    description = "Create a Model, Resource Model, Collection, Repository, Interfaces, and UI Components."

    def add(self, name=None, table=None, fields="", admin_grid=False, api=False, **kwargs):
        # 1. Map Legacy Arguments
        if 'model_name' in kwargs and not name: name = kwargs['model_name']
        if 'web_api' in kwargs: api = kwargs['web_api']
        if 'adminhtml_grid' in kwargs: admin_grid = kwargs['adminhtml_grid']
        
        if 'field_name' in kwargs and 'field_type' in kwargs:
            legacy_field = f"{kwargs['field_name']}:{kwargs['field_type']}"
            if fields:
                fields = f"{fields},{legacy_field}"
            else:
                fields = legacy_field

        if not name:
            raise ValueError("Model name is required.")

        model_name = upperfirst(name)
        module_package = self._module.package
        module_name = self._module.name
        
        # 2. Parse Fields
        field_list = []
        id_field = f"{name.lower()}_id"
        # Add ID field first (needed for DB schema and Model)
        field_list.append({'name': id_field, 'type': 'int', 'required': False})
        
        if fields:
            for f in fields.split(','):
                parts = f.split(':')
                fname = parts[0].strip()
                ftype = parts[1].strip() if len(parts) > 1 else 'string'
                field_list.append({'name': fname, 'type': ftype, 'required': True})

        table_name = table if table else f"{module_package.lower()}_{module_name.lower()}_{name.lower()}"
        
        # 3. Context Preparation
        processed_fields = [] # Contains ALL fields (for PHP classes)
        ui_fields = []        # Contains ONLY non-ID fields (for Grid/Form loops)
        
        for f in field_list:
            p_type = get_php_type(f['type'], f['required'])
            field_data = {
                'name': f['name'],
                'const': f['name'].upper(),
                'method_name': "".join([x.capitalize() for x in f['name'].split('_')]),
                'var_name': lowerfirst("".join([x.capitalize() for x in f['name'].split('_')])),
                'php_type': p_type,
                'doc_type': get_php_doc_type(f['type'], f['required']),
                'cast_type': p_type.replace('?', ''),
            }
            processed_fields.append(field_data)
            
            # Logic: Exclude ID from UI components to prevent duplication
            if f['name'] != id_field:
                ui_fields.append(field_data)

        base_context = {
            'package': module_package,
            'module': module_name,
            'model_name': model_name,
            'fields': processed_fields,
            'table_name': table_name,
            'id_field': id_field,
            'event_prefix': table_name,
        }

        # 4. Generate Interfaces
        interface_name = f"{model_name}Interface"
        extension_interface = f"{model_name}ExtensionInterface"
        interface_ns = f"{module_package}\\{module_name}\\Api\\Data"
        
        content = TemplateEngine.render('snippets/model/interface.j2', {
            **base_context,
            'namespace': interface_ns,
            'class_name': interface_name,
            'extension_interface': extension_interface
        })
        self.add_static_file("Api/Data", StaticFile(f"{interface_name}.php", body=content))

        search_results_interface = f"{model_name}SearchResultsInterface"
        content = TemplateEngine.render('snippets/model/search_results.j2', {
            'namespace': interface_ns,
            'class_name': search_results_interface,
            'model_name': model_name,
            'interface_namespace': interface_ns,
            'interface_name': interface_name
        })
        self.add_static_file("Api/Data", StaticFile(f"{search_results_interface}.php", body=content))

        repo_interface = f"{model_name}RepositoryInterface"
        repo_ns = f"{module_package}\\{module_name}\\Api"
        content = TemplateEngine.render('snippets/model/repository_interface.j2', {
            'namespace': repo_ns,
            'class_name': repo_interface,
            'model_name': model_name,
            'interface_namespace': interface_ns,
            'interface_name': interface_name,
            'var_name': lowerfirst(model_name),
            'id_field': 'id'
        })
        self.add_static_file("Api", StaticFile(f"{repo_interface}.php", body=content))

        # 5. Generate Model
        model_ns = f"{module_package}\\{module_name}\\Model"
        resource_name = f"{model_name}"
        resource_ns = f"{module_package}\\{module_name}\\Model\\ResourceModel"
        
        content = TemplateEngine.render('snippets/model/model.j2', {
            **base_context,
            'namespace': model_ns,
            'class_name': model_name,
            'interface_namespace': interface_ns,
            'interface_name': interface_name,
            'resource_namespace': resource_ns,
            'resource_name': resource_name,
            'extension_interface': f"{interface_ns}\\{extension_interface}"
        })
        self.add_static_file("Model", StaticFile(f"{model_name}.php", body=content))

        # 6. Resource Model
        content = TemplateEngine.render('snippets/model/resource.j2', {
            'namespace': resource_ns,
            'class_name': resource_name,
            'table_name': table_name,
            'id_field': id_field
        })
        self.add_static_file("Model/ResourceModel", StaticFile(f"{resource_name}.php", body=content))

        # 7. Collection
        collection_name = "Collection"
        collection_ns = f"{resource_ns}\\{model_name}"
        
        content = TemplateEngine.render('snippets/model/collection.j2', {
            'namespace': collection_ns,
            'class_name': collection_name,
            'model_namespace': model_ns,
            'model_name': model_name,
            'resource_namespace': resource_ns,
            'resource_name': resource_name,
            'id_field': id_field
        })
        self.add_static_file(f"Model/ResourceModel/{model_name}", StaticFile(f"{collection_name}.php", body=content))

        # 8. Repository Implementation
        repo_class = f"{model_name}Repository"
        content = TemplateEngine.render('snippets/model/repository.j2', {
            'namespace': model_ns,
            'class_name': repo_class,
            'repository_interface': f"{repo_ns}\\{repo_interface}",
            'interface_namespace': interface_ns,
            'interface_name': interface_name,
            'model_name': model_name,
            'resource_namespace': resource_ns,
            'resource_name': resource_name,
            'collection_namespace': collection_ns,
            'collection_name': collection_name,
            'var_name': lowerfirst(model_name),
            'id_field': 'id'
        })
        self.add_static_file("Model", StaticFile(f"{repo_class}.php", body=content))

        # 9. Schema
        db_table = Table(table_name, comment=f"{model_name} Table")
        for f in field_list:
            if f['name'] == id_field:
                db_table.add_column(f['name'], 'integer', identity=True, unsigned=True, nullable=False, comment="Entity ID")
                db_table.add_primary_key(f['name'])
            else:
                db_table.add_column(f['name'], f['type'], nullable=True, comment=f['name'])

        schema_node = Xmlnode('schema', 
            attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd"},
            nodes=[db_table.to_xml_node()]
        )
        self.add_xml('etc/db_schema.xml', schema_node)
        
        # 10. DI Preferences
        di_node = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
            Xmlnode('preference', attributes={'for': f"{repo_ns}\\{repo_interface}", 'type': f"{model_ns}\\{repo_class}"}),
            Xmlnode('preference', attributes={'for': f"{interface_ns}\\{interface_name}", 'type': f"{model_ns}\\{model_name}"}),
            Xmlnode('preference', attributes={'for': f"{interface_ns}\\{search_results_interface}", 'type': 'Magento\\Framework\\Api\\SearchResults'})
        ])
        self.add_xml('etc/di.xml', di_node)

        self.add_static_file('.', Readme(specifications=f" - Model: {model_name} ({table_name})"))

        # 11. Admin Grid / Form / Menu
        if admin_grid:
            route_id = f"{module_package.lower()}_{module_name.lower()}"
            model_lower = model_name.lower()
            
            # A. Menu
            menu_xml_str = TemplateEngine.render('snippets/model/menu.j2', {
                'package': module_package,
                'module_name': f"{module_package}_{module_name}",
                'table_name': table_name,
                'model_name': model_name,
                'module': module_name,
                'route_id': route_id,
                'model_lower': model_lower
            })
            self.add_static_file('etc/adminhtml', StaticFile('menu.xml', body=menu_xml_str))
            
            # B. UI Listing (Using filtered ui_fields)
            listing_xml = TemplateEngine.render('snippets/model/listing.j2', {
                'table_name': table_name,
                'model_name': model_name,
                'id_field': id_field,
                'fields': ui_fields, # Corrected: ui_fields
                'package': module_package,
                'module': module_name,
                'route_id': route_id,
                'model_lower': model_lower
            })
            self.add_static_file(f"view/adminhtml/ui_component", StaticFile(f"{table_name}_listing.xml", body=listing_xml))
            
            # C. UI Form (Using filtered ui_fields)
            form_xml = TemplateEngine.render('snippets/model/form.j2', {
                'table_name': table_name,
                'model_name': model_name,
                'id_field': id_field,
                'fields': ui_fields, # Corrected: ui_fields
                'package': module_package,
                'module': module_name
            })
            self.add_static_file(f"view/adminhtml/ui_component", StaticFile(f"{table_name}_form.xml", body=form_xml))
            
            # D. Actions Column
            actions_name = f"{model_name}Actions"
            actions_ns = f"{module_package}\\{module_name}\\Ui\\Component\\Listing\\Column"
            actions_content = TemplateEngine.render('snippets/model/actions.j2', {
                'namespace': actions_ns,
                'class_name': actions_name,
                'id_field': id_field,
                'route_id': route_id,
                'model_lower': model_lower
            })
            self.add_static_file(f"Ui/Component/Listing/Column", StaticFile(f"{actions_name}.php", body=actions_content))
            
            # E. Data Provider
            dp_name = "DataProvider"
            dp_ns = f"{model_ns}\\{model_name}"
            dp_content = TemplateEngine.render('snippets/model/dataprovider.j2', {
                'namespace': dp_ns,
                'collection_class': f"{collection_ns}\\{collection_name}",
                'register_key': table_name
            })
            self.add_static_file(f"Model/{model_name}", StaticFile(f"{dp_name}.php", body=dp_content))
            
            # F. Layouts
            layout_content = TemplateEngine.render('snippets/model/layout.j2', {
                'ui_component': f"{table_name}_listing"
            })
            self.add_static_file(f"view/adminhtml/layout", StaticFile(f"{route_id}_{model_lower}_index.xml", body=layout_content))
            
            layout_edit = TemplateEngine.render('snippets/model/layout.j2', {
                'ui_component': f"{table_name}_form"
            })
            self.add_static_file(f"view/adminhtml/layout", StaticFile(f"{route_id}_{model_lower}_edit.xml", body=layout_edit))
            
            layout_new = f"""<?xml version="1.0"?>
<page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="urn:magento:framework:View/Layout/etc/page_configuration.xsd">
    <update handle="{route_id}_{model_lower}_edit"/>
</page>"""
            self.add_static_file(f"view/adminhtml/layout", StaticFile(f"{route_id}_{model_lower}_new.xml", body=layout_new))

        self.add_static_file('.', Readme(specifications=f" - Admin Grid/Form: {model_name}"))
