from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class SystemDynamicRowSnippet(Snippet):
    snippet_label = 'System Config Dynamic Row'
    description = "Add a Dynamic Row configuration field."

    def add(self, 
        tab, section, group, field,
        columns, # Format: id:Label,id:Label
        default_value="",
        create_tab=False
    ):
        # 1. Parse Columns
        # Input: "name:Name,age:Age"
        col_list = []
        if columns:
            for col in columns.split(','):
                parts = col.split(':')
                col_id = parts[0].strip()
                col_label = parts[1].strip() if len(parts) > 1 else upperfirst(col_id)
                col_list.append({'id': col_id, 'label': col_label, 'class': 'required-entry'})

        # 2. Generate Frontend Model (Block)
        block_name = f"{upperfirst(field)}Row"
        ns_block = f"{self._module.package}\\{self._module.name}\\Block\\Adminhtml\\System\\Config\\Field"
        frontend_model = f"{ns_block}\\{block_name}"
        
        content = TemplateEngine.render('snippets/system/dynamic_row.j2', {
            'namespace': ns_block,
            'class_name': block_name,
            'columns': col_list
        })
        self.add_static_file(f"Block/Adminhtml/System/Config/Field/{block_name}.php", StaticFile(f"{block_name}.php", body=content))

        # 3. System XML (Reuse logic logic via Xmlnode construction)
        resource_id = f"{self.module_name}::config_{section.lower()}"
        
        system_node = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
            Xmlnode('system', nodes=[
                Xmlnode('section', attributes={'id': section.lower()}, nodes=[
                    Xmlnode('group', attributes={'id': group.lower()}, nodes=[
                        Xmlnode('field', attributes={'id': field.lower(), 'type': 'text', 'translate': 'label', 'sortOrder': '10', 'showInDefault': '1', 'showInWebsite': '1', 'showInStore': '1'}, nodes=[
                            Xmlnode('label', node_text=upperfirst(field)),
                            Xmlnode('frontend_model', node_text=frontend_model),
                            Xmlnode('backend_model', node_text='Magento\\Config\\Model\\Config\\Backend\\Serialized\\ArraySerialized')
                        ])
                    ])
                ])
            ])
        ])
        
        if create_tab:
            tab_node = Xmlnode('tab', attributes={'id': tab.lower(), 'translate': 'label', 'sortOrder': '100'}, nodes=[
                Xmlnode('label', node_text=upperfirst(tab))
            ])
            system_node.nodes[0].nodes.insert(0, tab_node)

        self.add_xml('etc/adminhtml/system.xml', system_node)
        
        # ACL
        acl_node = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:Acl/etc/acl.xsd"}, nodes=[
            Xmlnode('acl', nodes=[
                Xmlnode('resources', nodes=[
                    Xmlnode('resource', attributes={'id': 'Magento_Backend::admin'}, nodes=[
                        Xmlnode('resource', attributes={'id': 'Magento_Backend::stores'}, nodes=[
                            Xmlnode('resource', attributes={'id': 'Magento_Backend::stores_settings'}, nodes=[
                                Xmlnode('resource', attributes={'id': 'Magento_Config::config'}, nodes=[
                                    Xmlnode('resource', attributes={'id': resource_id, 'title': upperfirst(section)})
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ])
        self.add_xml('etc/acl.xml', acl_node)

        self.add_static_file('.', Readme(specifications=f" - Config Dynamic Row: {section}/{group}/{field}"))