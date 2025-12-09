import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst, lowerfirst, merge_xml_files
from ..schema import Table, Constraint
from ..types import get_php_type, get_php_doc_type

class ModelSnippet(Snippet):
    snippet_label = 'Model (CRUD)'
    description = "Create a Model, Resource Model, Collection, Repository, Interfaces, and UI Components."

    def _get_graphql_type(self, type_str):
        mapping = {
            'int': 'Int',
            'integer': 'Int',
            'smallint': 'Int',
            'tinyint': 'Int',
            'bigint': 'Int',
            'boolean': 'Boolean',
            'bool': 'Boolean',
            'float': 'Float',
            'decimal': 'Float',
            'numeric': 'Float',
        }
        return mapping.get(type_str, 'String')

    def add(self, name=None, table=None, fields="", admin_grid=False, api=False, graphql=False, menu_parent=None, **kwargs):
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

        if menu_parent is None:
            menu_parent = kwargs.get('menu_parent')

        model_name = upperfirst(name)
        module_package = self._module.package
        module_name = self._module.name
        
        # 2. Parse Fields
        field_list = []
        id_field = f"{name.lower()}_id"
        field_list.append({'name': id_field, 'type': 'int', 'required': False})
        
        # Track special field types
        has_is_active = False
        image_fields = []
        serializing_fields = [] 
        
        # Dictionary to store foreign key definitions: {field_name: {table, column, label}}
        foreign_keys = {}

        if fields:
            for f in fields.split(','):
                parts = f.split(':')
                fname = parts[0].strip()
                ftype = parts[1].strip() if len(parts) > 1 else 'string'
                
                # Auto-assign Source Models
                fsource = ''
                if ftype == 'boolean' or fname == 'is_active':
                    fsource = 'Magento\\Config\\Model\\Config\\Source\\Yesno'
                    if fname == 'is_active':
                        has_is_active = True
                
                # Check for Foreign Key Syntax: product_id:int:foreign=table.id.label
                if len(parts) > 2 and parts[2].startswith('foreign='):
                    # Parse: foreign=catalog_product_entity.entity_id.sku
                    ref_def = parts[2].split('=')[1]
                    ref_parts = ref_def.split('.')
                    
                    ref_table = ref_parts[0]
                    ref_col = ref_parts[1] if len(ref_parts) > 1 else 'entity_id'
                    ref_label = ref_parts[2] if len(ref_parts) > 2 else 'name' # Default label column
                    
                    foreign_keys[fname] = {
                        'table': ref_table,
                        'column': ref_col,
                        'label': ref_label
                    }
                    
                    # Generate Source Model Class Name
                    source_class_name = f"{upperfirst(fname)}Options"
                    source_ns = f"{module_package}\\{module_name}\\Model\\Config\\Source"
                    fsource = f"{source_ns}\\{source_class_name}"
                    
                    # Create Source Model File immediately
                    source_content = TemplateEngine.render('snippets/model/source.j2', {
                        'namespace': source_ns,
                        'class_name': source_class_name,
                        'table': ref_table,
                        'id_col': ref_col,
                        'label_col': ref_label
                    })
                    self.add_static_file(f"Model/Config/Source/{source_class_name}", StaticFile(f"{source_class_name}.php", body=source_content))

                
                # Identify complex fields
                if ftype == 'image':
                    image_fields.append(fname)
                if ftype == 'multiselect':
                    serializing_fields.append(fname)
                
                field_list.append({'name': fname, 'type': ftype, 'required': True, 'source': fsource})

        table_name = table if table else f"{module_package.lower()}_{module_name.lower()}_{name.lower()}"
        
        # 3. Context Preparation
        processed_fields = []
        ui_fields = []        
        
        for f in field_list:
            p_type = get_php_type(f['type'], f['required'])
            graphql_type = self._get_graphql_type(f['type'])
            
            # --- Smart UI Mapping ---
            ui_type = 'text'
            form_element = 'input'
            data_type = 'text'

            # Logic: If it has a source model (from foreign key or bool/select), use Select
            if f.get('source'):
                ui_type = 'select'
                form_element = 'select'
            
            if f['type'] in ['date', 'datetime']: 
                ui_type = 'date'
                form_element = 'date'
            elif f['type'] == 'boolean': 
                ui_type = 'boolean'
                form_element = 'checkbox'
                data_type = 'boolean'
            elif f['type'] == 'image': 
                ui_type = 'thumbnail'
                form_element = 'fileUploader'
            elif f['type'] in ['textarea', 'mediumtext']:
                form_element = 'textarea'
                if 'html' in f['name']: form_element = 'wysiwyg'

            field_data = {
                'name': f['name'],
                'label': upperfirst(f['name'].replace('_', ' ')),
                'const': f['name'].upper(),
                'method_name': "".join([x.capitalize() for x in f['name'].split('_')]),
                'var_name': lowerfirst("".join([x.capitalize() for x in f['name'].split('_')])),
                'php_type': p_type,
                'graphql_type': graphql_type,
                'doc_type': get_php_doc_type(f['type'], f['required']),
                'cast_type': p_type.replace('?', ''),
                'ui_type': ui_type,
                'form_element': form_element,
                'data_type': data_type,
                'source_model': f.get('source', ''),
                'required': f['required']
            }
            processed_fields.append(field_data)
            
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

        # 1. Interfaces
        interface_name = f"{model_name}Interface"
        extension_interface = f"{model_name}ExtensionInterface"
        interface_ns = f"{module_package}\\{module_name}\\Api\\Data"
        content = TemplateEngine.render('snippets/model/interface.j2', {**base_context, 'namespace': interface_ns, 'class_name': interface_name, 'extension_interface': extension_interface})
        self.add_static_file("Api/Data", StaticFile(f"{interface_name}.php", body=content))

        search_results_interface = f"{model_name}SearchResultsInterface"
        content = TemplateEngine.render('snippets/model/search_results.j2', {'namespace': interface_ns, 'class_name': search_results_interface, 'model_name': model_name, 'interface_namespace': interface_ns, 'interface_name': interface_name})
        self.add_static_file("Api/Data", StaticFile(f"{search_results_interface}.php", body=content))

        repo_interface = f"{model_name}RepositoryInterface"
        repo_ns = f"{module_package}\\{module_name}\\Api"
        content = TemplateEngine.render('snippets/model/repository_interface.j2', {'namespace': repo_ns, 'class_name': repo_interface, 'model_name': model_name, 'interface_namespace': interface_ns, 'interface_name': interface_name, 'var_name': lowerfirst(model_name), 'id_field': 'id'})
        self.add_static_file("Api", StaticFile(f"{repo_interface}.php", body=content))

        # 2. Model
        model_ns = f"{module_package}\\{module_name}\\Model"
        resource_name = f"{model_name}"
        resource_ns = f"{module_package}\\{module_name}\\Model\\ResourceModel"
        content = TemplateEngine.render('snippets/model/model.j2', {**base_context, 'namespace': model_ns, 'class_name': model_name, 'interface_namespace': interface_ns, 'interface_name': interface_name, 'resource_namespace': resource_ns, 'resource_name': resource_name, 'extension_interface': f"{interface_ns}\\{extension_interface}"})
        self.add_static_file("Model", StaticFile(f"{model_name}.php", body=content))

        # 3. Resource Model
        content = TemplateEngine.render('snippets/model/resource.j2', {
            'namespace': resource_ns,
            'class_name': resource_name,
            'table_name': table_name,
            'id_field': id_field,
            'image_fields': image_fields,
            'serializing_fields': serializing_fields
        })
        self.add_static_file("Model/ResourceModel", StaticFile(f"{resource_name}.php", body=content))

        # 4. Collection
        collection_name = "Collection"
        collection_ns = f"{resource_ns}\\{model_name}"
        content = TemplateEngine.render('snippets/model/collection.j2', {'namespace': collection_ns, 'class_name': collection_name, 'model_namespace': model_ns, 'model_name': model_name, 'resource_namespace': resource_ns, 'resource_name': resource_name, 'id_field': id_field})
        self.add_static_file(f"Model/ResourceModel/{model_name}", StaticFile(f"{collection_name}.php", body=content))

        # 5. Repository
        repo_class = f"{model_name}Repository"
        content = TemplateEngine.render('snippets/model/repository.j2', {'namespace': model_ns, 'class_name': repo_class, 'repository_interface': f"{repo_ns}\\{repo_interface}", 'interface_namespace': interface_ns, 'interface_name': interface_name, 'model_name': model_name, 'resource_namespace': resource_ns, 'resource_name': resource_name, 'collection_namespace': collection_ns, 'collection_name': collection_name, 'var_name': lowerfirst(model_name), 'id_field': 'id'})
        self.add_static_file("Model", StaticFile(f"{repo_class}.php", body=content))

        # 6. Schema & DI (Updated with Constraints)
        db_table = Table(table_name, comment=f"{model_name} Table")
        for f in field_list:
            if f['name'] == id_field:
                db_table.add_column(f['name'], 'integer', identity=True, unsigned=True, nullable=False, comment="Entity ID")
                db_table.add_primary_key(f['name'])
            else:
                db_type = 'varchar' if f['type'] == 'image' else f['type']
                if f['type'] == 'multiselect': db_type = 'text' 
                
                # Determine nullability and constraints
                is_nullable = True
                
                # If foreign key, type matches parent (usually int), and add constraint
                if f['name'] in foreign_keys:
                    fk_data = foreign_keys[f['name']]
                    fk_const = Constraint(Constraint.FOREIGN, referenceId=f"FK_{table_name}_{f['name']}")
                    fk_const.attributes['table'] = table_name
                    fk_const.attributes['column'] = f['name']
                    fk_const.attributes['referenceTable'] = fk_data['table']
                    fk_const.attributes['referenceColumn'] = fk_data['column']
                    fk_const.attributes['onDelete'] = 'CASCADE'
                    fk_const.add_column(f['name'])
                    
                    db_table.add_constraint(fk_const)
                    
                    # Foreign keys are usually integers
                    if db_type == 'string': db_type = 'int'
                    # Add Index for FK
                    idx = Constraint(Constraint.UNIQUE, referenceId=f"IDX_{table_name}_{f['name']}") # Using Constraint class as Index generic or dedicated
                    # (Assuming Table schema supports Index object or generic node addition. 
                    # The current schema.py has Index class, let's use it properly)
                    # Note: Mage2Gen schema.py Index class usage:
                    # idx = Index(referenceId=...)
                    # idx.add_column(...)
                    # db_table.add_index(idx)
                    # For simplicity in snippet, we rely on the DB to index FKs or add explicitly if needed.
                
                db_table.add_column(f['name'], db_type, nullable=is_nullable, comment=f['name'])

        schema_node = Xmlnode('schema', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd"}, nodes=[db_table.to_xml_node()])
        self.add_xml('etc/db_schema.xml', schema_node)
        
        di_nodes = [
            Xmlnode('preference', attributes={'for': f"{repo_ns}\\{repo_interface}", 'type': f"{model_ns}\\{repo_class}"}),
            Xmlnode('preference', attributes={'for': f"{interface_ns}\\{interface_name}", 'type': f"{model_ns}\\{model_name}"}),
            Xmlnode('preference', attributes={'for': f"{interface_ns}\\{search_results_interface}", 'type': 'Magento\\Framework\\Api\\SearchResults'})
        ]
        
        # --- IMAGE UPLOAD LOGIC ---
        if image_fields:
            uploader_type_name = f"{module_package}\\{module_name}\\{model_name}ImageUploader"
            upload_dir = f"{module_package.lower()}/{model_name.lower()}"
            di_nodes.append(Xmlnode('virtualType', attributes={'name': uploader_type_name, 'type': 'Magento\\Catalog\\Model\\ImageUploader'}, nodes=[
                Xmlnode('arguments', nodes=[
                    Xmlnode('argument', attributes={'name': 'baseTmpPath', 'xsi:type': 'string'}, node_text=f"{upload_dir}/tmp"),
                    Xmlnode('argument', attributes={'name': 'basePath', 'xsi:type': 'string'}, node_text=upload_dir),
                    Xmlnode('argument', attributes={'name': 'allowedExtensions', 'xsi:type': 'array'}, nodes=[
                        Xmlnode('item', attributes={'name': 'jpg', 'xsi:type': 'string'}, node_text='jpg'),
                        Xmlnode('item', attributes={'name': 'jpeg', 'xsi:type': 'string'}, node_text='jpeg'),
                        Xmlnode('item', attributes={'name': 'gif', 'xsi:type': 'string'}, node_text='gif'),
                        Xmlnode('item', attributes={'name': 'png', 'xsi:type': 'string'}, node_text='png')
                    ]),
                    Xmlnode('argument', attributes={'name': 'allowedMimeTypes', 'xsi:type': 'array'}, nodes=[
                        Xmlnode('item', attributes={'name': 'jpg', 'xsi:type': 'string'}, node_text='image/jpg'),
                        Xmlnode('item', attributes={'name': 'jpeg', 'xsi:type': 'string'}, node_text='image/jpeg'),
                        Xmlnode('item', attributes={'name': 'gif', 'xsi:type': 'string'}, node_text='image/gif'),
                        Xmlnode('item', attributes={'name': 'png', 'xsi:type': 'string'}, node_text='image/png')
                    ])
                ])
            ]))
            admin_ctrl_ns = f"{module_package}\\{module_name}\\Controller\\Adminhtml\\{upperfirst(name)}"
            di_nodes.append(Xmlnode('type', attributes={'name': f"{admin_ctrl_ns}\\Upload"}, nodes=[
                Xmlnode('arguments', nodes=[
                    Xmlnode('argument', attributes={'name': 'imageUploader', 'xsi:type': 'object'}, node_text=uploader_type_name)
                ])
            ]))

        di_xml = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=di_nodes)
        self.add_xml('etc/di.xml', di_xml)

        self.add_static_file('.', Readme(specifications=f" - Model: {model_name} ({table_name})"))

        # --- ADMIN GRID / FORM LOGIC ---
        if admin_grid:
            route_id = f"{module_package.lower()}_{module_name.lower()}"
            model_lower = model_name.lower()
            
            parent_id = menu_parent if menu_parent else f"{module_package}::top_level"
            menu_xml_str = TemplateEngine.render('snippets/model/menu.j2', {
                'package': module_package, 'module_name': f"{module_package}_{module_name}", 'table_name': table_name,
                'model_name': model_name, 'module': module_name, 'route_id': route_id, 'model_lower': model_lower,
                'menu_parent': menu_parent, 'parent_id': parent_id
            })
            self.add_static_file('etc/adminhtml', StaticFile('menu.xml', body=menu_xml_str))

            listing_xml = TemplateEngine.render('snippets/model/listing.j2', {'table_name': table_name, 'model_name': model_name, 'id_field': id_field, 'fields': ui_fields, 'package': module_package, 'module': module_name, 'route_id': route_id, 'model_lower': model_lower, 'has_is_active': has_is_active})
            self.add_static_file(f"view/adminhtml/ui_component", StaticFile(f"{table_name}_listing.xml", body=listing_xml))

            form_xml = TemplateEngine.render('snippets/model/form.j2', {
                'table_name': table_name, 'model_name': model_name, 'id_field': id_field, 'fields': ui_fields,
                'package': module_package, 'module': module_name, 'route_id': route_id, 'model_lower': model_lower
            })
            self.add_static_file(f"view/adminhtml/ui_component", StaticFile(f"{table_name}_form.xml", body=form_xml))

            actions_name = f"{model_name}Actions"
            actions_ns = f"{module_package}\\{module_name}\\Ui\\Component\\Listing\\Column"
            actions_content = TemplateEngine.render('snippets/model/actions.j2', {'namespace': actions_ns, 'class_name': actions_name, 'id_field': id_field, 'route_id': route_id, 'model_lower': model_lower})
            self.add_static_file(f"Ui/Component/Listing/Column", StaticFile(f"{actions_name}.php", body=actions_content))

            dp_name = "DataProvider"
            dp_ns = f"{model_ns}\\{model_name}"
            dp_content = TemplateEngine.render('snippets/model/dataprovider.j2', {
                'namespace': dp_ns, 'collection_class': f"{collection_ns}\\{collection_name}", 'register_key': table_name,
                'image_fields': image_fields, 'module_path': f"{module_package.lower()}/{model_name.lower()}"
            })
            self.add_static_file(f"Model/{model_name}", StaticFile(f"{dp_name}.php", body=dp_content))

            admin_ctrl_ns = f"{module_package}\\{module_name}\\Controller\\Adminhtml\\{upperfirst(name)}"
            mass_delete_content = TemplateEngine.render('snippets/controller/admin/mass_delete.j2', {'namespace': admin_ctrl_ns, 'resource_id': f"{module_package}_{module_name}::{model_lower}", 'collection_class': f"{collection_ns}\\{collection_name}", 'repository_interface': f"{repo_ns}\\{repo_interface}"})
            self.add_static_file(f"Controller/Adminhtml/{upperfirst(name)}", StaticFile("MassDelete.php", body=mass_delete_content))

            if has_is_active:
                for status_label, status_value in [('Enable', 'true'), ('Disable', 'false')]:
                    content = TemplateEngine.render('snippets/controller/admin/mass_status.j2', {'namespace': admin_ctrl_ns, 'resource_id': f"{module_package}_{module_name}::{model_lower}", 'collection_class': f"{collection_ns}\\{collection_name}", 'repository_interface': f"{repo_ns}\\{repo_interface}", 'status_label': status_label, 'status_value': status_value})
                    self.add_static_file(f"Controller/Adminhtml/{upperfirst(name)}", StaticFile(f"Mass{status_label}.php", body=content))

            if image_fields:
                upload_content = TemplateEngine.render('snippets/controller/admin/upload.j2', {
                    'namespace': admin_ctrl_ns, 'resource_id': f"{module_package}_{module_name}::{model_lower}", 'field_name': image_fields[0]
                })
                self.add_static_file(f"Controller/Adminhtml/{upperfirst(name)}", StaticFile("Upload.php", body=upload_content))

            layout_content = TemplateEngine.render('snippets/model/layout.j2', {'ui_component': f"{table_name}_listing"})
            self.add_static_file(f"view/adminhtml/layout", StaticFile(f"{route_id}_{model_lower}_index.xml", body=layout_content))
            layout_edit = TemplateEngine.render('snippets/model/layout.j2', {'ui_component': f"{table_name}_form"})
            self.add_static_file(f"view/adminhtml/layout", StaticFile(f"{route_id}_{model_lower}_edit.xml", body=layout_edit))
            layout_new = f"""<?xml version="1.0"?><page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="urn:magento:framework:View/Layout/etc/page_configuration.xsd"><update handle="{route_id}_{model_lower}_edit"/></page>"""
            self.add_static_file(f"view/adminhtml/layout", StaticFile(f"{route_id}_{model_lower}_new.xml", body=layout_new))

        self.add_static_file('.', Readme(specifications=f" - Admin Grid/Form: {model_name}"))

        # --- GRAPHQL LOGIC ---
        if graphql:
            resolver_ns = f"{module_package}\\{module_name}\\Model\\Resolver\\{model_name}"
            
            # Common resolver context
            res_context = {
                'namespace': resolver_ns,
                'repository_interface': f"{repo_ns}\\{repo_interface}",
                'repository_short': repo_interface,
                'id_field': id_field
            }

            # 1. Resolvers
            # Get
            content = TemplateEngine.render('snippets/graphql/crud/resolver_get.j2', res_context)
            self.add_static_file(f"Model/Resolver/{model_name}", StaticFile("Get.php", body=content))
            
            # List
            content = TemplateEngine.render('snippets/graphql/crud/resolver_list.j2', res_context)
            self.add_static_file(f"Model/Resolver/{model_name}", StaticFile("ListResolver.php", body=content))
            
            # Save
            content = TemplateEngine.render('snippets/graphql/crud/resolver_save.j2', {
                **res_context, 
                'model_factory': f"{interface_ns}\\{interface_name}Factory",
                'model_factory_short': f"{interface_name}Factory"
            })
            self.add_static_file(f"Model/Resolver/{model_name}", StaticFile("Save.php", body=content))
            
            # Delete
            content = TemplateEngine.render('snippets/graphql/crud/resolver_delete.j2', res_context)
            self.add_static_file(f"Model/Resolver/{model_name}", StaticFile("Delete.php", body=content))

            # 2. Schema
            type_name = model_name
            id_type = 'Int' # Default for auto-increment ID
            
            # Generate Schema
            schema_content = TemplateEngine.render('snippets/graphql/crud/schema.j2', {
                'query_name': lowerfirst(model_name),
                'query_list_name': lowerfirst(model_name) + 'List',
                'id_field': id_field,
                'id_type': id_type,
                'type_name': type_name,
                'model_name': model_name,
                'resolver_get': f"{resolver_ns}\\Get",
                'resolver_list': f"{resolver_ns}\\ListResolver",
                'resolver_save': f"{resolver_ns}\\Save",
                'resolver_delete': f"{resolver_ns}\\Delete",
                'fields': processed_fields
            })
            
            self.add_static_file('etc', StaticFile('schema.graphqls', body=schema_content))
            
            # 3. Module Sequence
            seq_config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
                Xmlnode('module', attributes={'name': f"{module_package}_{module_name}"}, nodes=[
                    Xmlnode('sequence', attributes={}, nodes=[
                        Xmlnode('module', attributes={'name': 'Magento_GraphQl'})
                    ])
                ])
            ])
            self.add_xml('etc/module.xml', seq_config)
            
            self.add_static_file('.', Readme(specifications=f" - GraphQL CRUD: {model_name}"))