import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class BlockSnippet(Snippet):
    snippet_label = 'Block'
    description = "Create a Block, Layout XML, and PHTML template."

    def add(self, name, layout_handle, reference="content", **kwargs):
        package = self._module.package
        module = self._module.name
        
        block_name = upperfirst(name)
        namespace = f"{package}\\{module}\\Block"
        block_class_full = f"{namespace}\\{block_name}"
        
        # 1. Generate Block PHP
        content = TemplateEngine.render('snippets/block/block.j2', {
            'namespace': namespace,
            'class_name': block_name
        })
        self.add_static_file(f"Block/{block_name}", StaticFile(f"{block_name}.php", body=content))

        # 2. Generate PHTML Template
        template_file = f"{name.lower()}.phtml"
        template_path = f"{package}_{module}::{template_file}"
        
        phtml_content = TemplateEngine.render('snippets/block/template.j2', {
            'block_var': 'block',
            'block_class': block_class_full
        })
        self.add_static_file(f"view/frontend/templates/{template_file}", StaticFile(template_file, body=phtml_content))

        # 3. Generate Layout XML
        page = Xmlnode('page', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
            Xmlnode('body', attributes={}, nodes=[
                Xmlnode('referenceContainer', attributes={'name': reference}, nodes=[
                    Xmlnode('block', attributes={
                        'class': block_class_full,
                        'name': f"{package.lower()}_{module.lower()}_{name.lower()}",
                        'template': template_path
                    })
                ])
            ])
        ])
        
        self.add_xml(f"view/frontend/layout/{layout_handle}.xml", page)

        self.add_static_file(
            '.',
            Readme(
                specifications=f" - Block: {block_name} ({layout_handle})",
            )
        )