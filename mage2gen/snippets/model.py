import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst, lowerfirst, merge_xml_files
from ..schema import Table
from ..types import get_php_type, get_php_doc_type

class ModelSnippet(Snippet):
    snippet_label = 'Model (CRUD)'
    description = "Create a Model, Resource Model, Collection, Repository, Interfaces, and UI Components."

    def add(self, name=None, table=None, fields="", admin_grid=False, api=False, menu_parent=None, **kwargs):
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
        
        # Track if we have a status field for Mass Actions
        has_is_active = False
        image_fields = [] # Track image fields
        
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
                
                if ftype == 'image':
                    image_fields.append(fname)
                
                field_list.append({'name': fname, 'type': ftype, 'required': True, 'source': fsource})

        table_name = table if table else f"{module_package.lower()}_{module_name.lower()}_{name.lower()}"
        
        # 3. Context Preparation (ENHANCED FOR FORM)
        processed_fields = []
        ui_fields = []        
        
        for f in field_list:
            p_type = get_php_type(f['type'], f['required'])
            
            # --- Smart UI Mapping ---
            # Grid Column Type
            ui_type = 'text'
            if f['type'] in ['date', 'datetime']: ui_type = 'date'
            elif f['type'] == 'boolean': ui_type = 'boolean'
            elif f['type'] in ['select', 'multiselect']: ui_type = 'select'
            elif f['type'] == 'image': ui_type = 'thumbnail'

            # Form Element Mapping
            form_element = 'input'
            data_type = 'text'
            
            if f['type'] == 'image':
                form_element = 'fileUploader'
            elif f['type'] == 'boolean':
                form_element = 'checkbox'
                data_type = 'boolean'
            elif f['type'] in ['date', 'datetime']:
                form_element = 'date'
                data_type = 'text' # Date components use text dataType but date formElement
            elif f['type'] in ['select', 'multiselect']:
                form_element = 'select'
                data_type = 'text'
            elif f['type'] in ['textarea', 'mediumtext', 'longtext']:
                form_element = 'textarea'
                if 'html' in f['name']: # Heuristic for WYSIWYG
                    form_element = 'wysiwyg'

            field_data = {
                'name': f['name'],
                'label': upperfirst(f['name'].replace('_', ' ')),
                'const': f['name'].upper(),
                'method_name': "".join([x.capitalize() for x in f['name'].split('_')]),
                'var_name': lowerfirst("".join([x.capitalize() for x in f['name'].split('_')])),
                'php_type': p_type,
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

        # 2. Model, Resource, Collection
        model_ns = f"{module_package}\\{module_name}\\Model"
        resource_name = f"{model_name}"
        resource_ns = f"{module_package}\\{module_name}\\Model\\ResourceModel"
        content = TemplateEngine.render('snippets/model/model.j2', {**base_context, 'namespace': model_ns, 'class_name': model_name, 'interface_namespace': interface_ns, 'interface_name': interface_name, 'resource_namespace': resource_ns, 'resource_name': resource_name, 'extension_interface': f"{interface_ns}\\{extension_interface}"})
        self.add_static_file("Model", StaticFile(f"{model_name}.php", body=content))

        content = TemplateEngine.render('snippets/model/resource.j2', {'namespace': resource_ns, 'class_name': resource_name, 'table_name': table_name, 'id_field': id_field})
        self.add_static_file("Model/ResourceModel", StaticFile(f"{resource_name}.php", body=content))

        collection_name = "Collection"
        collection_ns = f"{resource_ns}\\{model_name}"
        content = TemplateEngine.render('snippets/model/collection.j2', {'namespace': collection_ns, 'class_name': collection_name, 'model_namespace': model_ns, 'model_name': model_name, 'resource_namespace': resource_ns, 'resource_name': resource_name, 'id_field': id_field})
        self.add_static_file(f"Model/ResourceModel/{model_name}", StaticFile(f"{collection_name}.php", body=content))

        # 3. Repository
        repo_class = f"{model_name}Repository"
        content = TemplateEngine.render('snippets/model/repository.j2', {'namespace': model_ns, 'class_name': repo_class, 'repository_interface': f"{repo_ns}\\{repo_interface}", 'interface_namespace': interface_ns, 'interface_name': interface_name, 'model_name': model_name, 'resource_namespace': resource_ns, 'resource_name': resource_name, 'collection_namespace': collection_ns, 'collection_name': collection_name, 'var_name': lowerfirst(model_name), 'id_field': 'id'})
        self.add_static_file("Model", StaticFile(f"{repo_class}.php", body=content))

        # 4. Schema & DI
        db_table = Table(table_name, comment=f"{model_name} Table")
        for f in field_list:
            if f['name'] == id_field:
                db_table.add_column(f['name'], 'integer', identity=True, unsigned=True, nullable=False, comment="Entity ID")
                db_table.add_primary_key(f['name'])
            else:
                db_type = 'varchar' if f['type'] == 'image' else f['type']
                db_table.add_column(f['name'], db_type, nullable=True, comment=f['name'])
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
            
            # 1. Add Virtual Type for Uploader
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
            
            # 2. Inject Uploader into Controller
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
            
            # Determine Parent Menu
            parent_id = f"{module_package}::top_level"
            if menu_parent:
                parent_id = menu_parent

            # A. Menu
            menu_xml_str = TemplateEngine.render('snippets/model/menu.j2', {
                'package': module_package,
                'module_name': f"{module_package}_{module_name}",
                'table_name': table_name,
                'model_name': model_name,
                'module': module_name,
                'route_id': route_id,
                'model_lower': model_lower,
                'menu_parent': menu_parent,
                'parent_id': parent_id
            })
            self.add_static_file('etc/adminhtml', StaticFile('menu.xml', body=menu_xml_str))
            
            # B. UI Listing
            listing_xml = TemplateEngine.render('snippets/model/listing.j2', {
                'table_name': table_name,
                'model_name': model_name,
                'id_field': id_field,
                'fields': ui_fields, 
                'package': module_package,
                'module': module_name,
                'route_id': route_id,
                'model_lower': model_lower,
                'has_is_active': has_is_active # To optionally render MassActions
            })
            self.add_static_file(f"view/adminhtml/ui_component", StaticFile(f"{table_name}_listing.xml", body=listing_xml))
            
            # C. Smart UI Form
            form_xml = TemplateEngine.render('snippets/model/form.j2', {
                'table_name': table_name,
                'model_name': model_name,
                'id_field': id_field,
                'fields': ui_fields, # Contains form_element and data_type
                'package': module_package,
                'module': module_name,
                'route_id': route_id,
                'model_lower': model_lower # Passed for upload URL generation
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
                'register_key': table_name,
                'image_fields': image_fields,
                'module_path': f"{module_package.lower()}/{model_name.lower()}"
            })
            self.add_static_file(f"Model/{model_name}", StaticFile(f"{dp_name}.php", body=dp_content))
            
            # E. Mass Delete Controller
            admin_ctrl_ns = f"{module_package}\\{module_name}\\Controller\\Adminhtml\\{upperfirst(name)}"
            
            mass_delete_content = TemplateEngine.render('snippets/controller/admin/mass_delete.j2', {
                'namespace': admin_ctrl_ns,
                'resource_id': f"{module_package}_{module_name}::{model_lower}",
                'collection_class': f"{collection_ns}\\{collection_name}",
                'repository_interface': f"{repo_ns}\\{repo_interface}"
            })
            self.add_static_file(f"Controller/Adminhtml/{upperfirst(name)}", StaticFile("MassDelete.php", body=mass_delete_content))

            # F. Mass Enable/Disable Controllers
            if has_is_active:
                for status_label, status_value in [('Enable', 'true'), ('Disable', 'false')]:
                    content = TemplateEngine.render('snippets/controller/admin/mass_status.j2', {
                        'namespace': admin_ctrl_ns,
                        'resource_id': f"{module_package}_{module_name}::{model_lower}",
                        'collection_class': f"{collection_ns}\\{collection_name}",
                        'repository_interface': f"{repo_ns}\\{repo_interface}",
                        'status_label': status_label,
                        'status_value': status_value
                    })
                    self.add_static_file(f"Controller/Adminhtml/{upperfirst(name)}", StaticFile(f"Mass{status_label}.php", body=content))

            # G. Image Upload Controller
            if image_fields:
                upload_content = TemplateEngine.render('snippets/controller/admin/upload.j2', {
                    'namespace': admin_ctrl_ns,
                    'resource_id': f"{module_package}_{module_name}::{model_lower}",
                    'field_name': image_fields[0] # Default fallback
                })
                self.add_static_file(f"Controller/Adminhtml/{upperfirst(name)}", StaticFile("Upload.php", body=upload_content))

            # H. Layouts
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