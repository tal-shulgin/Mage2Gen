from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class LoggerSnippet(Snippet):
    snippet_label = 'Logger'
    description = "Create a custom Logger and Handler."

    def add(self, name, filename="custom.log", **kwargs):
        package = self._module.package
        module = self._module.name
        
        logger_name = upperfirst(name)
        handler_name = f"{logger_name}Handler"
        
        ns_logger = f"{package}\\{module}\\Logger"
        ns_handler = f"{package}\\{module}\\Logger\\Handler"

        # Logger Class
        c_logger = TemplateEngine.render('snippets/logger/logger.j2', {
            'namespace': ns_logger,
            'class_name': logger_name
        })
        self.add_static_file("Logger", StaticFile(f"{logger_name}.php", body=c_logger))

        # Handler Class
        c_handler = TemplateEngine.render('snippets/logger/handler.j2', {
            'namespace': ns_handler,
            'class_name': handler_name,
            'file_name': filename
        })
        self.add_static_file("Logger/Handler", StaticFile(f"{handler_name}.php", body=c_handler))

        # DI XML
        config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
            Xmlnode('type', attributes={'name': f"{ns_handler}\\{handler_name}"}, nodes=[
                Xmlnode('arguments', nodes=[
                    Xmlnode('argument', attributes={'name': 'filesystem', 'xsi:type': 'object'}, node_text='Magento\\Framework\\Filesystem\\Driver\\File')
                ])
            ]),
            Xmlnode('type', attributes={'name': f"{ns_logger}\\{logger_name}"}, nodes=[
                Xmlnode('arguments', nodes=[
                    Xmlnode('argument', attributes={'name': 'name', 'xsi:type': 'string'}, node_text=name.lower()),
                    Xmlnode('argument', attributes={'name': 'handlers', 'xsi:type': 'array'}, nodes=[
                        Xmlnode('item', attributes={'name': 'system', 'xsi:type': 'object'}, node_text=f"{ns_handler}\\{handler_name}")
                    ])
                ])
            ])
        ])
        self.add_xml('etc/di.xml', config)

        self.add_static_file('.', Readme(specifications=f" - Logger: {name} -> {filename}"))