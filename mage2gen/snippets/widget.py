import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class WidgetSnippet(Snippet):
    snippet_label = 'Widget'
    description = "Create a Frontend Widget."

    def add(self, name, field, field_type='text', sortorder=10, **kwargs):
        package = self._module.package
        module = self._module.name
        
        class_name = upperfirst(name)
        namespace = f"{package}\\{module}\\Block\\Widget"
        template_file = f"{name.lower()}.phtml"
        
        # 1. Block Class
        content = TemplateEngine.render('snippets/widget/block.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'template_file': template_file
        })
        self.add_static_file(f"Block/Widget/{class_name}", StaticFile(f"{class_name}.php", body=content))

        # 2. PHTML Template
        phtml_body = f"""<?php if($block->getData('{field.lower()}')): ?>
    <h2 class='{field.lower()}'><?= $escaper->escapeHtml($block->getData('{field.lower()}')) ?></h2>
<?php endif; ?>"""
        
        # Explicit path handling
        self.add_static_file(f"view/frontend/templates/widget", StaticFile(template_file, body=phtml_body))

        # 3. Widget XML
        parameter_attributes = {'name': field.lower(),'xsi:type': field_type,'visible': 'true','sort_order': str(sortorder)}
        if field_type in ['select', 'multiselect']:
            parameter_attributes["source_model"] = "Magento\\Config\\Model\\Config\\Source\\Yesno"

        widget_xml = Xmlnode('widgets',attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Widget:etc/widget.xsd"},nodes=[
            Xmlnode('widget',attributes={'id':f'{package.lower()}_{module.lower()}_{name.lower()}','class':f"{namespace}\\{class_name}"},nodes=[
                Xmlnode('label',node_text=name),
                Xmlnode('description',node_text=name),
                Xmlnode('parameters',nodes=[
                    Xmlnode('parameter', attributes=parameter_attributes, nodes=[
                        Xmlnode('label',node_text=field)
                    ])
                ])  
            ])
        ])
        self.add_xml('etc/widget.xml', widget_xml)

        self.add_static_file('.', Readme(specifications=f" - Widget: {name}"))