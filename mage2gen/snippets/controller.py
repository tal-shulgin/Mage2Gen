import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class ControllerSnippet(Snippet):
    snippet_label = 'Controller'
    description = "Create a Controller Action and Route."

    def add(self, frontname=None, section='index', action='index', adminhtml=False, **kwargs):
        # Support legacy 'admin' kwarg from tests if present
        if 'admin' in kwargs:
            adminhtml = kwargs['admin']
        
        # Legacy map
        admin = adminhtml 
        
        package = self._module.package
        module = self._module.name
        
        if not frontname:
            frontname = f"{package.lower()}_{module.lower()}"

        # 1. Generate Controller Class
        namespace_parts = [package, module, "Controller"]
        if admin:
            namespace_parts.append("Adminhtml")
        
        namespace_parts.append(upperfirst(section))
        namespace = "\\".join(namespace_parts)
        class_name = upperfirst(action)
        
        content = TemplateEngine.render('snippets/controller/controller.j2', {
            'namespace': namespace,
            'class_name': class_name
        })
        
        path_parts = ["Controller"]
        if admin:
            path_parts.append("Adminhtml")
        path_parts.append(upperfirst(section))
        path = "/".join(path_parts)
        
        self.add_static_file(f"{path}/{class_name}", StaticFile(f"{class_name}.php", body=content))

        # 2. Generate Routes XML
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

        self.add_static_file(
            '.',
            Readme(
                specifications=f" - Controller: {frontname}/{section}/{action}",
            )
        )