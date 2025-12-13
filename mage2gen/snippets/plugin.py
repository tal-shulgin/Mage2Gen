import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class PluginSnippet(Snippet):
    snippet_label = 'Plugin'
    description = "Create a Before/After/Around Plugin."

    def add(self, target_class, method, type="after", sort_order=10, **kwargs):
        # [FIX] Support 'plugin_type' alias to avoid YAML collision with component 'type'
        if 'plugin_type' in kwargs:
            type = kwargs['plugin_type']

        package = self._module.package
        module = self._module.name
        
        target_parts = target_class.split('\\')
        clean_target = "".join([x.capitalize() for x in target_parts if x])
        plugin_name = f"{clean_target}Plugin"
        
        namespace = f"{package}\\{module}\\Plugin"
        
        # 1. Generate PHP
        content = TemplateEngine.render('snippets/plugin/plugin.j2', {
            'namespace': namespace,
            'class_name': plugin_name,
            'subject_class': target_class,
            'method_name': method,
            'type': type
        })
        self.add_static_file("Plugin", StaticFile(f"{plugin_name}.php", body=content))

        # 2. Generate DI XML
        config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
            Xmlnode('type', attributes={'name': target_class}, nodes=[
                Xmlnode('plugin', attributes={
                    'name': f"{package}_{module}_Plugin_{clean_target}",
                    'type': f"{namespace}\\{plugin_name}",
                    'sortOrder': str(sort_order),
                    'disabled': 'false'
                })
            ])
        ])
        
        self.add_xml("etc/di.xml", config)

        self.add_static_file(
            '.',
            Readme(
                specifications=f" - Plugin: {plugin_name} ({type} {method})",
            )
        )