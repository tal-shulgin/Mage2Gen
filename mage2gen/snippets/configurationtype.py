import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class ConfigurationTypeSnippet(Snippet):
    snippet_label = 'Configuration Type'
    description = "Create a custom XML configuration file type (e.g. events.xml, routes.xml logic)."

    def add(self, config_name, node_name, field_name, extra_params=None):
        config_class_name = ''.join(upperfirst(w) for w in config_name.split('_'))
        package = self._module.package
        module = self._module.name
        
        namespace = f"{package}\\{module}\\Config\\{config_class_name}"
        
        # 1. XSD Generation
        config_xsd = Xmlnode('xs:schema', xsd=True, attributes={'attributeFormDefault':"unqualified", "elementFormDefault":"qualified", "xmlns:xs":"http://www.w3.org/2001/XMLSchema"}, nodes=[
            Xmlnode('xs:element', attributes={'name': 'config'}, nodes=[
                Xmlnode('xs:complexType', nodes=[
                    Xmlnode('xs:choice', attributes={'maxOccurs': 'unbounded'}, nodes=[
                        Xmlnode('xs:element', attributes={'name': node_name, 'type': '{}Type'.format(node_name), 'maxOccurs': 'unbounded', 'minOccurs': '0'})
                    ])
                ])
            ]),
            Xmlnode('xs:complexType', attributes={'type': '{}Type'.format(node_name)}, nodes=[
                Xmlnode('xs:sequence', nodes=[
                    Xmlnode('xs:element', attributes={'name': field_name, 'type': 'xs:string'})
                ])
            ])  
        ])
        self.add_xml('etc/{}.xsd'.format(config_name), config_xsd)

        # 2. Merged XSD
        config_merged_xsd = Xmlnode('xs:schema', attributes={'xmlns:xs':'http://www.w3.org/2001/XMLSchema'}, nodes=[
            Xmlnode('xs:include', attributes={'schemaLocation': 'urn:magento:module:{}:etc/{}.xsd'.format(self.module_name, config_name)})
        ])
        self.add_xml('etc/{}_merged.xsd'.format(config_name), config_merged_xsd)

        # 3. Schema Locator
        loc_content = TemplateEngine.render('snippets/config/schema_locator.j2', {
            'namespace': namespace,
            'class_name': 'SchemaLocator',
            'module_name': self.module_name,
            'config_name': config_name
        })
        self.add_static_file(f"Config/{config_class_name}", StaticFile("SchemaLocator.php", body=loc_content))

        # 4. Converter
        conv_content = TemplateEngine.render('snippets/config/converter.j2', {
            'namespace': namespace,
            'class_name': 'Converter',
            'node_name': node_name
        })
        self.add_static_file(f"Config/{config_class_name}", StaticFile("Converter.php", body=conv_content))

        # 5. Reader
        reader_content = TemplateEngine.render('snippets/config/reader.j2', {
            'namespace': namespace,
            'class_name': 'Reader',
            'node_name': node_name,
            'config_name': config_name
        })
        self.add_static_file(f"Config/{config_class_name}", StaticFile("Reader.php", body=reader_content))

        self.add_static_file('.', Readme(specifications=f" - Configuration Type: {config_name}"))