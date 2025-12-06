import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst, lowerfirst
from ..schema import Table
from ..types import get_php_type, get_php_doc_type

class ModelSnippet(Snippet):
    snippet_label = 'Model (CRUD)'
    description = "Create a Model, Resource Model, Collection, Repository, and Interfaces."

    def add(self, name=None, table=None, fields="", admin_grid=False, api=False, **kwargs):
        # 1. Map Legacy Arguments
        if 'model_name' in kwargs and not name: name = kwargs['model_name']
        if 'web_api' in kwargs: api = kwargs['web_api']
        if 'adminhtml_grid' in kwargs: admin_grid = kwargs['adminhtml_grid']
        
        # Handle legacy single-field input (field_name, field_type)
        if 'field_name' in kwargs and 'field_type' in kwargs:
            legacy_field = f"{kwargs['field_name']}:{kwargs['field_type']}"
            if fields:
                fields = f"{fields},{legacy_field}"
            else:
                fields = legacy_field

        if not name:
            raise ValueError("Model name is required (use 'name' or 'model_name').")

        model_name = upperfirst(name)
        module_package = self._module.package
        module_name = self._module.name
        
        # 2. Parse Fields
        field_list = []
        id_field = f"{name.lower()}_id"
        field_list.append({
            'name': id_field,
            'type': 'int', 
            'required': False
        })
        
        if fields:
            for f in fields.split(','):
                parts = f.split(':')
                fname = parts[0]
                ftype = parts[1] if len(parts) > 1 else 'string'
                field_list.append({
                    'name': fname,
                    'type': ftype,
                    'required': True
                })

        table_name = table if table else f"{module_package.lower()}_{module_name.lower()}_{name.lower()}"
        
        # 3. Prepare Context
        processed_fields = []
        for f in field_list:
            p_type = get_php_type(f['type'], f['required'])
            processed_fields.append({
                'name': f['name'],
                'const': f['name'].upper(),
                'method_name': "".join([x.capitalize() for x in f['name'].split('_')]),
                'var_name': lowerfirst("".join([x.capitalize() for x in f['name'].split('_')])),
                'php_type': p_type,
                'doc_type': get_php_doc_type(f['type'], f['required']),
                'cast_type': p_type.replace('?', ''),
            })

        base_context = {
            'package': module_package,
            'module': module_name,
            'model_name': model_name,
            'fields': processed_fields,
            'table_name': table_name,
            'id_field': id_field,
            'event_prefix': table_name,
        }

        # 4. Generate Interface
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

        # 6. Generate Resource Model
        content = TemplateEngine.render('snippets/model/resource.j2', {
            'namespace': resource_ns,
            'class_name': resource_name,
            'table_name': table_name,
            'id_field': id_field
        })
        self.add_static_file("Model/ResourceModel", StaticFile(f"{resource_name}.php", body=content))

        # 7. Generate Collection
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

        # 8. Generate DB Schema
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

        self.add_static_file('.', Readme(specifications=f" - Model: {model_name} ({table_name})"))