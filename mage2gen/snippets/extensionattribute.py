import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst, to_pascal_case
from ..schema import Table

class ExtensionAttributeSnippet(Snippet):
    snippet_label = 'Extension Attribute'
    description = "Add an Extension Attribute to an existing Interface with optional persistence."

    def add(self, interface, code, type='string', repository=None, table=None, **kwargs):
        if not code:
            raise ValueError("Attribute code is required.")
        if not interface:
            raise ValueError("Target Interface is required.")

        package = self._module.package
        module = self._module.name
        
        # 1. Generate extension_attributes.xml
        ext_xml = Xmlnode('config', attributes={
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Api/etc/extension_attributes.xsd"
        }, nodes=[
            Xmlnode('extension_attributes', attributes={'for': interface}, nodes=[
                Xmlnode('attribute', attributes={'code': code, 'type': type})
            ])
        ])
        self.add_xml('etc/extension_attributes.xml', ext_xml)

        # 2. Persistence Logic (If Repository & Table provided)
        if repository and table:
            # A. DB Schema (Add column to existing table)
            db_type = 'varchar'
            if type in ['int', 'integer']: db_type = 'int'
            elif type in ['bool', 'boolean']: db_type = 'smallint'
            elif type == 'float': db_type = 'float'
            
            # Note: In a real scenario, we merge schema. 
            # Here we generate a schema node for the column.
            schema_node = Xmlnode('schema', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd"}, nodes=[
                Xmlnode('table', attributes={'name': table}, nodes=[
                    Xmlnode('column', attributes={'name': code, 'xsi:type': db_type, 'nullable': 'true', 'comment': f'{code} extension attribute'})
                ])
            ])
            self.add_xml('etc/db_schema.xml', schema_node)

            # B. Generate Repository Plugin
            interface_parts = interface.split('\\')
            entity_name = interface_parts[-1].replace('Interface', '') # e.g. Customer
            
            plugin_class_name = f"{entity_name}RepositoryPlugin"
            namespace = f"{package}\\{module}\\Plugin"
            
            # Logic to construct CamelCase code for setters/getters
            code_camel = to_pascal_case(code)
            
            # Data Interface for the Extension (Magento convention)
            # Usually: Interface + 'ExtensionInterface'
            extension_interface = f"{interface}ExtensionInterface"

            content = TemplateEngine.render('snippets/extension_attribute/plugin.j2', {
                'namespace': namespace,
                'class_name': plugin_class_name,
                'interface': extension_interface,
                'repository': repository,
                'entity_interface': interface,
                'code': code,
                'code_camel': code_camel,
                'type': type
            })
            self.add_static_file("Plugin", StaticFile(f"{plugin_class_name}.php", body=content))

            # C. Register Plugin in DI.xml
            di_config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
                Xmlnode('type', attributes={'name': repository}, nodes=[
                    Xmlnode('plugin', attributes={
                        'name': f"{package}_{module}_{entity_name}ExtensionAttribute",
                        'type': f"{namespace}\\{plugin_class_name}",
                        'sortOrder': '10'
                    })
                ])
            ])
            self.add_xml('etc/di.xml', di_config)

        self.add_static_file('.', Readme(specifications=f" - Extension Attribute: {code} ({type}) for {interface}"))