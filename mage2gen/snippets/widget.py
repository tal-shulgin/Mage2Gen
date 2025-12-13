import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class WidgetSnippet(Snippet):
    snippet_label = 'Widget'
    description = "Create a Frontend Widget."

    def add(self, name, field=None, field_type='text', sortorder=10, fields=None, **kwargs):
        package = self._module.package
        module = self._module.name
        
        class_name = upperfirst(name)
        namespace = f"{package}\\{module}\\Block\\Widget"
        template_file = f"{name.lower()}.phtml"
        
        # Normalize fields into a list
        # If 'fields' list is provided in YAML, use it.
        # If legacy 'field' arg is provided, wrap it.
        all_fields = []
        
        if fields and isinstance(fields, list):
            all_fields = fields
        elif field:
            all_fields.append({
                'name': field, 
                'type': field_type, 
                'label': field
            })
            
        if not all_fields:
            # Fallback/Default if nothing provided
            all_fields.append({'name': 'title', 'type': 'text', 'label': 'Title'})

        # 1. Block Class
        content = TemplateEngine.render('snippets/widget/block.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'template_file': template_file
        })
        self.add_static_file(f"Block/Widget/{class_name}", StaticFile(f"{class_name}.php", body=content))

        # 2. PHTML Template (Dynamic generation for all fields)
        phtml_lines = []
        for f in all_fields:
            fname = f.get('name', 'unknown').lower()
            flabel = f.get('label', fname)
            
            phtml_lines.append(f"<!-- {flabel} -->")
            phtml_lines.append(f"<?php if($block->getData('{fname}')): ?>")
            phtml_lines.append(f"    <div class='widget-{fname}'>")
            phtml_lines.append(f"        <?= $escaper->escapeHtml($block->getData('{fname}')) ?>")
            phtml_lines.append(f"    </div>")
            phtml_lines.append(f"<?php endif; ?>\n")
            
        self.add_static_file(f"view/frontend/templates/widget", StaticFile(template_file, body="\n".join(phtml_lines)))

        # 3. Widget XML
        parameter_nodes = []
        current_sort = sortorder
        
        for f in all_fields:
            p_name = f.get('name', '').lower()
            p_type = f.get('type', 'text')
            p_label = f.get('label', upperfirst(p_name))
            
            attr = {
                'name': p_name,
                'xsi:type': p_type,
                'visible': 'true',
                'sort_order': str(current_sort)
            }
            
            if p_type in ['select', 'multiselect']:
                # Default to Yes/No if no source provided (simplified logic)
                attr["source_model"] = f.get('source_model', "Magento\\Config\\Model\\Config\\Source\\Yesno")

            parameter_nodes.append(
                Xmlnode('parameter', attributes=attr, nodes=[
                    Xmlnode('label', node_text=p_label)
                ])
            )
            current_sort += 10

        widget_xml = Xmlnode('widgets', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Widget:etc/widget.xsd"}, nodes=[
            Xmlnode('widget', attributes={'id':f'{package.lower()}_{module.lower()}_{name.lower()}','class':f"{namespace}\\{class_name}"}, nodes=[
                Xmlnode('label', node_text=name),
                Xmlnode('description', node_text=name),
                Xmlnode('parameters', nodes=parameter_nodes)  
            ])
        ])
        self.add_xml('etc/widget.xml', widget_xml)

        self.add_static_file('.', Readme(specifications=f" - Widget: {name} ({len(all_fields)} fields)"))