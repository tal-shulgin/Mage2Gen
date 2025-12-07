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
        depends=None,
        **kwargs
    ):
        original_type = field_type
        type = field_type
        
        # Data Preparation
        tab_data = {'id': tab.lower(), 'label': upperfirst(tab), 'sortOrder': 100} if create_tab else {'id': tab}
        section_data = {'id': section.lower(), 'label': upperfirst(section), 'sortOrder': 10, 'showInDefault': 1, 'showInWebsite': 1, 'showInStore': 1}
        group_data = {'id': group.lower(), 'label': upperfirst(group), 'sortOrder': 10, 'showInDefault': 1, 'showInWebsite': 1, 'showInStore': 1}
        
        # Source Model mapping
        source_model = ''
        backend_model = ''
        frontend_model = ''
        upload_dir_node = None
        
        if type in ['select', 'multiselect']:
            source_model = 'Magento\\Config\\Model\\Config\\Source\\Yesno'
        elif type == 'email':
            # Magento's default source model for email templates
            source_model = 'Magento\\Config\\Model\\Config\\Source\\Email\\Template'
            type = 'select'

        elif type == 'image':
            # Image Upload Logic
            backend_class_name = f"{upperfirst(field)}Image"
            ns_backend = f"{self._module.package}\\{self._module.name}\\Model\\Config\\Backend"
            backend_model = f"{ns_backend}\\{backend_class_name}"
            
            content = TemplateEngine.render('snippets/system/backend_image.j2', {
                'namespace': ns_backend,
                'class_name': backend_class_name,
                'upload_dir': f"{section}/{group}"
            })
            self.add_static_file(f"Model/Config/Backend/{backend_class_name}.php", StaticFile(f"{backend_class_name}.php", body=content))
            upload_dir_node = Xmlnode('upload_dir', attributes={'config': 'system/filesystem/media', 'scope_info': '1'}, node_text=f"{section}/{group}")
            
        elif type == 'color':
            # Color Picker Logic
            type = 'text'
            frontend_class_name = f"{upperfirst(field)}Color"
            ns_frontend = f"{self._module.package}\\{self._module.name}\\Block\\Adminhtml\\System\\Config\\Field"
            frontend_model = f"{ns_frontend}\\{frontend_class_name}"
            
            content = TemplateEngine.render('snippets/system/frontend_color.j2', {
                'namespace': ns_frontend,
                'class_name': frontend_class_name
            })
            self.add_static_file(f"Block/Adminhtml/System/Config/Field/{frontend_class_name}.php", StaticFile(f"{frontend_class_name}.php", body=content))

        resource_id = f"{self.module_name}::config_{section.lower()}"

        # 1. System XML
        field_nodes = [
            Xmlnode('label', node_text=upperfirst(field))
        ]
        if source_model: field_nodes.append(Xmlnode('source_model', node_text=source_model))
        if backend_model: field_nodes.append(Xmlnode('backend_model', node_text=backend_model))
        if frontend_model: field_nodes.append(Xmlnode('frontend_model', node_text=frontend_model))
        if upload_dir_node: field_nodes.append(upload_dir_node)
        
        # Dependency Logic
        if depends:
            parts = depends.split(':')
            dep_field = parts[0]
            dep_val = parts[1] if len(parts) > 1 else '1'
            field_nodes.append(Xmlnode('depends', nodes=[
                Xmlnode('field', attributes={'id': dep_field}, node_text=dep_val)
            ]))

        system_node = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
            Xmlnode('system', nodes=[
                Xmlnode('section', attributes={'id': section.lower()}, nodes=[
                    Xmlnode('group', attributes={'id': group.lower()}, nodes=[
                        Xmlnode('field', attributes={'id': field.lower(), 'type': type, 'translate': 'label', 'sortOrder': '10', 'showInDefault': '1', 'showInWebsite': '1', 'showInStore': '1'}, nodes=field_nodes)
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

        # 3. Config XML
        if default_value:
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

        # 4. Email Template (Re-integration)
        if original_type == 'email':
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