from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class ShippingSnippet(Snippet):
    snippet_label = 'Shipping Method'
    description = "Creates a Shipping Carrier."

    def add(self, name):
        package = self._module.package
        module = self._module.name
        
        code = name.lower().replace(' ', '_')
        class_name = upperfirst(name.replace(' ', ''))
        namespace = f"{package}\\{module}\\Model\\Carrier"
        
        # 1. Model
        content = TemplateEngine.render('snippets/shipping/model.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'shipping_code': code
        })
        self.add_static_file(f"Model/Carrier/{class_name}", StaticFile(f"{class_name}.php", body=content))

        # 2. Config XML
        config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Store:etc/config.xsd"}, nodes=[
            Xmlnode('default', nodes=[
                Xmlnode('carriers', nodes=[
                    Xmlnode(code, nodes=[
                        Xmlnode('active', node_text='1'),
                        Xmlnode('model', node_text=f"{namespace}\\{class_name}"),
                        Xmlnode('title', node_text=name),
                        Xmlnode('name', node_text=name)
                    ])
                ])
            ])
        ])
        self.add_xml('etc/config.xml', config)

        self.add_static_file('.', Readme(specifications=f" - Shipping: {name} ({code})"))