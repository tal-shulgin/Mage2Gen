from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class PaymentSnippet(Snippet):
    snippet_label = 'Payment Method'
    description = "Creates an Offline Payment Method."

    def add(self, name):
        package = self._module.package
        module = self._module.name
        
        payment_code = name.lower().replace(' ', '_')
        class_name = upperfirst(name.replace(' ', ''))
        namespace = f"{package}\\{module}\\Model\\Payment"
        
        # 1. Model
        content = TemplateEngine.render('snippets/payment/model.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'payment_code': payment_code
        })
        self.add_static_file(f"Model/Payment/{class_name}", StaticFile(f"{class_name}.php", body=content))

        # 2. Config XML
        config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Store:etc/config.xsd"}, nodes=[
            Xmlnode('default', nodes=[
                Xmlnode('payment', nodes=[
                    Xmlnode(payment_code, nodes=[
                        Xmlnode('active', node_text='1'),
                        Xmlnode('model', node_text=f"{namespace}\\{class_name}"),
                        Xmlnode('title', node_text=name),
                        Xmlnode('group', node_text='offline')
                    ])
                ])
            ])
        ])
        self.add_xml('etc/config.xml', config)
        
        # 3. System XML (Simplified for V3)
        system = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
            Xmlnode('system', nodes=[
                Xmlnode('section', attributes={'id': 'payment'}, nodes=[
                    Xmlnode('group', attributes={'id': payment_code, 'translate': 'label', 'sortOrder': '10', 'showInDefault': '1', 'showInWebsite': '1', 'showInStore': '1'}, nodes=[
                        Xmlnode('label', node_text=name),
                        Xmlnode('field', attributes={'id': 'active', 'translate': 'label', 'type': 'select', 'sortOrder': '10', 'showInDefault': '1', 'showInWebsite': '1', 'showInStore': '0'}, nodes=[
                            Xmlnode('label', node_text='Enabled'),
                            Xmlnode('source_model', node_text='Magento\\Config\\Model\\Config\\Source\\Yesno')
                        ]),
                        Xmlnode('field', attributes={'id': 'title', 'translate': 'label', 'type': 'text', 'sortOrder': '20', 'showInDefault': '1', 'showInWebsite': '1', 'showInStore': '1'}, nodes=[
                            Xmlnode('label', node_text='Title')
                        ])
                    ])
                ])
            ])
        ])
        self.add_xml('etc/adminhtml/system.xml', system)

        self.add_static_file('.', Readme(specifications=f" - Payment: {name} ({payment_code})"))