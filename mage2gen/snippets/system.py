from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class SystemSnippet(Snippet):
    snippet_label = 'System Config'
    description = "Add a System Configuration field with advanced options (scope, validation, encryption, rich types)."

    def _map_validation(self, validate_str):
        """Maps friendly aliases to Magento CSS validation classes."""
        if not validate_str:
            return None
            
        aliases = {
            'required': 'required-entry',
            'email': 'validate-email',
            'number': 'validate-number',
            'digits': 'validate-digits',
            'url': 'validate-url',
            'alpha': 'validate-alpha',
            'alphanum': 'validate-alphanum',
            'no-empty': 'no-whitespace',
            'zero-or-greater': 'validate-zero-or-greater'
        }
        
        classes = []
        for v in validate_str.split(','):
            v = v.strip()
            classes.append(aliases.get(v, v)) # Use alias if exists, else raw string
            
        return " ".join(classes)

    def add(self, 
        tab, section, group, field, 
        type="text", 
        scope="default,website,store",
        validate=None,
        comment=None,
        tooltip=None,
        can_restore=False,
        frontend_class=None,
        config_path=None,
        if_module_enabled=None,
        encrypt=False,
        default_value="", 
        create_tab=False,
        depends=None,
        **kwargs
    ):
        # Support legacy argument name 'field_type'
        if 'field_type' in kwargs: type = kwargs['field_type']
        
        original_type = type
        
        # Helper for class naming
        def camel_case(s):
            return "".join(x.capitalize() for x in s.split('_'))

        # 1. Scope Logic
        if scope == 'global':
            show_default, show_website, show_store = '1', '0', '0'
        else:
            show_default = '1' if 'default' in scope else '0'
            show_website = '1' if 'website' in scope else '0'
            show_store = '1' if 'store' in scope else '0'

        # 2. Validation Logic
        validation_classes = self._map_validation(validate)

        # 3. Source/Backend/Frontend Model Initialization
        source_model = kwargs.get('source_model', '')
        backend_model = kwargs.get('backend_model', '')
        frontend_model = kwargs.get('frontend_model', '')
        upload_dir_node = None
        
        # 4. Rich Type Logic
        if type in ['select', 'multiselect']:
            if not source_model:
                source_model = 'Magento\\Config\\Model\\Config\\Source\\Yesno'
                
        elif type == 'email':
            source_model = 'Magento\\Config\\Model\\Config\\Source\\Email\\Template'
            type = 'select'

        elif type == 'image':
            backend_class_name = f"{camel_case(field)}Image"
            ns_backend = f"{self._module.package}\\{self._module.name}\\Model\\Config\\Backend"
            backend_model = f"{ns_backend}\\{backend_class_name}"
            
            content = TemplateEngine.render('snippets/system/backend_image.j2', {
                'namespace': ns_backend,
                'class_name': backend_class_name,
                'upload_dir': f"{section}/{group}"
            })

            self.add_static_file("Model/Config/Backend", StaticFile(f"{backend_class_name}.php", body=content))
            upload_dir_node = Xmlnode('upload_dir', attributes={'config': 'system/filesystem/media', 'scope_info': '1'}, node_text=f"{section}/{group}")
            
        elif type == 'color':
            type = 'text'
            frontend_class_name = f"{camel_case(field)}Color"
            ns_frontend = f"{self._module.package}\\{self._module.name}\\Block\\Adminhtml\\System\\Config\\Field"
            frontend_model = f"{ns_frontend}\\{frontend_class_name}"
            
            content = TemplateEngine.render('snippets/system/frontend_color.j2', {
                'namespace': ns_frontend,
                'class_name': frontend_class_name
            })

            self.add_static_file("Block/Adminhtml/System/Config/Field", StaticFile(f"{frontend_class_name}.php", body=content))

        # 5. Encryption/Security Logic
        if encrypt or type == 'password':
            type = 'obscure'
            if not backend_model:
                backend_model = 'Magento\\Config\\Model\\Config\\Backend\\Encrypted'

        # --- XML Construction ---

        resource_id = f"{self.module_name}::config_{section.lower()}"

        # Build Field Nodes
        field_nodes = [
            Xmlnode('label', node_text=upperfirst(field.replace('_', ' ')))
        ]
        
        if comment: field_nodes.append(Xmlnode('comment', node_text=comment))
        if tooltip: field_nodes.append(Xmlnode('tooltip', node_text=tooltip))
        if validation_classes: field_nodes.append(Xmlnode('validate', node_text=validation_classes))
        if source_model: field_nodes.append(Xmlnode('source_model', node_text=source_model))
        if backend_model: field_nodes.append(Xmlnode('backend_model', node_text=backend_model))
        if frontend_model: field_nodes.append(Xmlnode('frontend_model', node_text=frontend_model))
        if upload_dir_node: field_nodes.append(upload_dir_node)
        
        if if_module_enabled: 
             field_nodes.append(Xmlnode('if_module_enabled', node_text=if_module_enabled))
        
        # Dependency Logic
        if depends:
            parts = depends.split(':')
            dep_field = parts[0]
            dep_val = parts[1] if len(parts) > 1 else '1'
            field_nodes.append(Xmlnode('depends', nodes=[
                Xmlnode('field', attributes={'id': dep_field}, node_text=dep_val)
            ]))

        # Field Attributes
        field_attrs = {
            'id': field.lower(), 
            'type': type, 
            'translate': 'label', 
            'sortOrder': '10', 
            'showInDefault': show_default, 
            'showInWebsite': show_website, 
            'showInStore': show_store
        }
        
        if can_restore:
            field_attrs['canRestore'] = '1'
        if frontend_class:
            field_attrs['frontend_class'] = frontend_class
        if config_path:
            field_attrs['config_path'] = config_path

        # 1. System XML
        system_node = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
            Xmlnode('system', nodes=[
                Xmlnode('section', attributes={'id': section.lower()}, nodes=[
                    Xmlnode('group', attributes={'id': group.lower()}, nodes=[
                        Xmlnode('field', attributes=field_attrs, nodes=field_nodes)
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

        # 3. Config XML (Avoid defaults for encrypted fields)
        if default_value and not encrypt:
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

        # 4. Email Template Logic
        if original_type == 'email':
            template_id = f"{section.lower()}_{group.lower()}_{field.lower()}"
            template_file = f"{field.lower()}.html"
            config_path = f"{section.lower()}/{group.lower()}/{field.lower()}"
            
            email_node = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Email:etc/email_templates.xsd"}, nodes=[
                Xmlnode('template', attributes={
                    'id': template_id,
                    'label': upperfirst(field),
                    'file': template_file,
                    'type': 'html',
                    'module': f"{self._module.package}_{self._module.name}",
                    'area': 'frontend'
                })
            ])
            self.add_xml('etc/email_templates.xml', email_node)
            
            html_content = TemplateEngine.render('snippets/system/email.html.j2', {
                'label': upperfirst(field),
                'field_id': field
            })
            self.add_static_file("view/frontend/email", StaticFile(template_file, body=html_content))

            helper_name = f"{camel_case(field)}Mail"
            namespace = f"{self._module.package}\\{self._module.name}\\Helper"
            
            helper_content = TemplateEngine.render('snippets/system/helper_mail.j2', {
                'namespace': namespace,
                'class_name': helper_name,
                'template_label': upperfirst(field),
                'method_name': camel_case(field),
                'config_path': config_path
            })
            self.add_static_file("Helper", StaticFile(f"{helper_name}.php", body=helper_content))

        specs = f" - Config: {section}/{group}/{field} [{type}]"
        if encrypt: specs += " (Encrypted)"
        if scope != "default,website,store": specs += f" Scope: {scope}"
        
        self.add_static_file('.', Readme(specifications=specs))