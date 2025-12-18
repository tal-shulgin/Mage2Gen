from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class ConsoleSnippet(Snippet):
    snippet_label = 'Console Command'
    description = "Create a bin/magento console command."

    def add(self, name, description="Sample command", instruction=None, **kwargs):
        package = self._module.package
        module = self._module.name
        
        if ':' in name:
            command_name = name
            class_part = "".join([x.capitalize() for x in name.split(':')])
        else:
            command_name = f"{package.lower()}:{module.lower()}:{name}"
            class_part = upperfirst(name)
            
        class_name = f"{class_part}Command"
        namespace = f"{package}\\{module}\\Console\\Command"
        
        content = TemplateEngine.render('snippets/console/command.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'command_name': command_name,
            'description': description,
            'instruction': instruction,
            'admin': False # Explicitly setting default as kwargs handling can be tricky
        })
        self.add_static_file("Console/Command", StaticFile(f"{class_name}.php", body=content))

        # DI XML
        config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
            Xmlnode('type', attributes={'name': r'Magento\Framework\Console\CommandList'}, nodes=[
                Xmlnode('arguments', nodes=[
                    Xmlnode('argument', attributes={'name':'commands', 'xsi:type':'array'}, nodes=[
                        Xmlnode('item', attributes={'name': command_name.replace(':','_'), 'xsi:type':'object'}, node_text=f"{namespace}\\{class_name}")
                    ])
                ])
            ])
        ])
        self.add_xml('etc/di.xml', config)

        self.add_static_file('.', Readme(specifications=f" - Console: {command_name}"))