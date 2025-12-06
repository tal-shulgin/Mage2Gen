from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class SystemSnippet(Snippet):
    snippet_label = 'System Config'
    description = "Add a System Configuration field."

    def add(self, 
        tab, section, group, field, 
        field_type="text", 
        default_value="", 
        create_tab=False,
        **kwargs
    ):
        type = field_type
        
        # Data Preparation
        tab_data = {'id': tab.lower(), 'label': upperfirst(tab), 'sortOrder': 100} if create_tab else {'id': tab}
        section_data = {'id': section.lower(), 'label': upperfirst(section), 'sortOrder': 10, 'showInDefault': 1, 'showInWebsite': 1, 'showInStore': 1}
        group_data = {'id': group.lower(), 'label': upperfirst(group), 'sortOrder': 10, 'showInDefault': 1, 'showInWebsite': 1, 'showInStore': 1}
        
        # Source Model mapping
        source_model = ''
        if type in ['select', 'multiselect']:
            source_model = 'Magento\\Config\\Model\\Config\\Source\\Yesno'
        elif type == 'email':
            # Magento's default source model for email templates
            source_model = 'Magento\\Config\\Model\\Config\\Source\\Email\\Template'
            # In system.xml, type is usually 'select' for email templates, not 'email'
            type = 'select'

        field_data = {
            'id': field.lower(),
            'label': upperfirst(field.replace('_', ' ')),
            'type': type,
            'sortOrder': 10,
            'showInDefault': 1, 'showInWebsite': 1, 'showInStore': 1,
            'comment': '',
            'source_model': source_model,
            'backend_model': ''
        }
        
        resource_id = f"{self.module_name}::config_{section.lower()}"

        # 1. System XML
        system_node = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
            Xmlnode('system', nodes=[
                Xmlnode('section', attributes={'id': section.lower()}, nodes=[
                    Xmlnode('group', attributes={'id': group.lower()}, nodes=[
                        Xmlnode('field', attributes={'id': field.lower(), 'type': type, 'translate': 'label', 'sortOrder': '10', 'showInDefault': '1', 'showInWebsite': '1', 'showInStore': '1'}, nodes=[
                            Xmlnode('label', node_text=upperfirst(field)),
                            Xmlnode('source_model', node_text=field_data['source_model']) if field_data['source_model'] else None
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

        # 2. ACL XML
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

        # 3. Config XML (Defaults)
        default_node = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Store:etc/config.xsd"}, nodes=[
            Xmlnode('default', nodes=[
                Xmlnode(section.lower(), nodes=[
                    Xmlnode(group.lower(), nodes=[
                        Xmlnode(field.lower(), node_text=default_value)
                    ])
                ])
            ])
        ])
        self.add_xml('etc/config.xml', default_node)

        # 4. Email Template Logic (Parity Restoration)
        if field_type == 'email':
            template_id = f"{section.lower()}_{group.lower()}_{field.lower()}"
            template_file = f"{field.lower()}.html"
            config_path = f"{section.lower()}/{group.lower()}/{field.lower()}"
            
            # Generate email_templates.xml
            email_node = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Email:etc/email_templates.xsd"}, nodes=[
                Xmlnode('template', attributes={
                    'id': template_id,
                    'label': upperfirst(field),
                    'file': template_file,
                    'type': 'html',
                    'module': self.module_name,
                    'area': 'frontend'
                })
            ])
            self.add_xml('etc/email_templates.xml', email_node)
            
            # Generate HTML Template
            html_content = TemplateEngine.render('snippets/system/email.html.j2', {
                'label': upperfirst(field),
                'field_id': field
            })
            self.add_static_file(f"view/frontend/email/{template_file}", StaticFile(template_file, body=html_content))

            # Generate Helper
            helper_name = f"{upperfirst(field)}Mail"
            namespace = f"{self._module.package}\\{self._module.name}\\Helper"
            
            helper_content = TemplateEngine.render('snippets/system/helper_mail.j2', {
                'namespace': namespace,
                'class_name': helper_name,
                'template_label': upperfirst(field),
                'method_name': upperfirst(field),
                'config_path': config_path
            })
            self.add_static_file(f"Helper/{helper_name}.php", StaticFile(f"{helper_name}.php", body=helper_content))

        self.add_static_file('.', Readme(specifications=f" - Config: {section}/{group}/{field}"))