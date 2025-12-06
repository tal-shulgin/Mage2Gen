from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class ApiSnippet(Snippet):
    snippet_label = 'API Endpoint'
    description = "Creates a REST API Endpoint."

    def add(self, name=None, method="GET", **kwargs):
        # Support legacy argument names from tests
        if name is None and 'api_name' in kwargs:
            name = kwargs['api_name']
        
        if 'api_method' in kwargs:
            method = kwargs['api_method']
            
        if not name:
            raise ValueError("API Name is required")

        package = self._module.package
        module = self._module.name
        
        name_clean = upperfirst(name)
        interface_name = f"{name_clean}Interface"
        model_name = name_clean
        
        # 1. Interface
        if_ns = f"{package}\\{module}\\Api"
        if_content = TemplateEngine.render('snippets/api/interface.j2', {
            'namespace': if_ns,
            'class_name': interface_name,
            'method_name': method.lower() + name_clean
        })
        self.add_static_file(f"Api/{interface_name}", StaticFile(f"{interface_name}.php", body=if_content))
        
        # 2. Model
        model_ns = f"{package}\\{module}\\Model"
        model_content = TemplateEngine.render('snippets/api/model.j2', {
            'namespace': model_ns,
            'class_name': model_name,
            'interface': f"\\{if_ns}\\{interface_name}",
            'interface_name_short': interface_name,
            'method_name': method.lower() + name_clean
        })
        self.add_static_file(f"Model/{model_name}", StaticFile(f"{model_name}.php", body=model_content))
        
        # 3. DI XML
        di = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
            Xmlnode('preference', attributes={'for': f"{if_ns}\\{interface_name}", 'type': f"{model_ns}\\{model_name}"})
        ])
        self.add_xml('etc/di.xml', di)
        
        # 4. WebAPI XML
        route_url = f"/V1/{package.lower()}-{module.lower()}/{name.lower()}"
        webapi = Xmlnode('routes', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Webapi:etc/webapi.xsd"}, nodes=[
            Xmlnode('route', attributes={'url': route_url, 'method': method}, nodes=[
                Xmlnode('service', attributes={'class': f"{if_ns}\\{interface_name}", 'method': method.lower() + name_clean}),
                Xmlnode('resources', nodes=[
                    Xmlnode('resource', attributes={'ref': 'anonymous'})
                ])
            ])
        ])
        self.add_xml('etc/webapi.xml', webapi)

        self.add_static_file('.', Readme(specifications=f" - API: {method} {route_url}"))