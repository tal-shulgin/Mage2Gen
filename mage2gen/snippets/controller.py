import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class ControllerSnippet(Snippet):
    snippet_label = 'Controller'
    description = "Create a Controller Action and Route (Logic Injected)."

    def add(self, frontname=None, section='index', action='index', adminhtml=False, 
            entity_context=None, instruction=None, **kwargs):
        
        if 'admin' in kwargs: adminhtml = kwargs['admin']
        admin = adminhtml 
        
        package = self._module.package
        module = self._module.name
        
        if not frontname:
            frontname = f"{package.lower()}_{module.lower()}"

        # 1. Determine Class Name and Namespace
        namespace_parts = [package, module, "Controller"]
        if admin:
            namespace_parts.append("Adminhtml")
        
        namespace_parts.append(upperfirst(section))
        namespace = "\\".join(namespace_parts)
        class_name = upperfirst(action)
        
        # 2. Logic Injection Strategy
        template = 'snippets/controller/controller.j2' # Default generic
        context_data = {
            'namespace': namespace,
            'class_name': class_name,
            'admin': admin,
            'parent_class': "\Magento\Backend\App\Action" if admin else "\Magento\Framework\App\Action\Action",
            'implements': "\Magento\Framework\App\Action\HttpGetActionInterface",
            'ctor_args': 'Context $context' if admin else 'PageFactory $resultPageFactory',
            'parent_call': 'parent::__construct($context);' if admin else '$this->resultPageFactory = $resultPageFactory;',
            'instruction': instruction # Pass to template
        }

        # Check if we have specific logic templates for Admin CRUD
        if admin and entity_context:
            action_lower = action.lower()
            
            # Common Context for CRUD
            crud_context = {
                'namespace': namespace,
                'class_name': class_name,
                'model_name': entity_context['model_name'],
                'model_namespace': entity_context['model_namespace'],
                'repository_interface': entity_context['repository_interface'],
                'id_field': entity_context['id_field'],
                'table_name': entity_context['table_name'],
                'resource_id': f"{package}_{module}::{entity_context['model_name']}"
            }
            
            if action_lower == 'save':
                template = 'snippets/controller/admin/save.j2'
                context_data = crud_context
            elif action_lower == 'delete':
                template = 'snippets/controller/admin/delete.j2'
                context_data = crud_context
            
            # Ensure dependencies are added to module context (Optional, if we tracked imports strictly)

        # 3. Generate File
        content = TemplateEngine.render(template, context_data)
        
        path_parts = ["Controller"]
        if admin:
            path_parts.append("Adminhtml")
        path_parts.append(upperfirst(section))
        path = "/".join(path_parts)

        self.add_static_file(path, StaticFile(f"{class_name}.php", body=content))

        # 4. Generate Routes XML (Standard Logic)
        area = "adminhtml" if admin else "frontend"
        router_id = "admin" if admin else "standard"
        
        module_node = Xmlnode('module', attributes={'name': f"{package}_{module}"})
        if admin:
            module_node.attributes['before'] = 'Magento_Backend'

        config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:App/etc/routes.xsd"}, nodes=[
            Xmlnode('router', attributes={'id': router_id}, nodes=[
                Xmlnode('route', attributes={'id': frontname, 'frontName': frontname}, nodes=[
                    module_node
                ])
            ])
        ])
        
        self.add_xml(f"etc/{area}/routes.xml", config)

        self.add_static_file('.', Readme(specifications=f" - Controller: {frontname}/{section}/{action}"))