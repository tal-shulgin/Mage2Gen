# A Magento 2 module generator library
# Copyright (C) 2025 Mage2Gen
import os
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme

class LoggerSnippet(Snippet):
    snippet_label = 'Logger'
    description = """
    Create a custom logger handler and logger class to log data to a specific file.
    """

    def add(self, logger_name, file_name='custom.log', extra_params=None):
        logger_name_capitalized = logger_name.capitalize()
        
        # 1. Create Logger Class
        logger_class = Phpclass(
            'Logger\\{}'.format(logger_name_capitalized),
            extends='\\Monolog\\Logger'
        )
        self.add_class(logger_class)

        # 2. Create Handler Class
        handler_class = Phpclass(
            'Logger\\Handler\\{}'.format(logger_name_capitalized),
            extends='\\Magento\\Framework\\Logger\\Handler\\Base',
            attributes=[
                '/**\n     * @var int\n     */\n    protected $loggerType = Logger::INFO;',
                '/**\n     * @var string\n     */\n    protected $fileName = \'/var/log/{}\';'.format(file_name)
            ],
            dependencies=['Monolog\\Logger']
        )
        self.add_class(handler_class)

        # 3. Create di.xml configuration
        di_xml = Xmlnode('config', attributes={
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:ObjectManager/etc/config.xsd"
        }, nodes=[
            Xmlnode('type', attributes={'name': handler_class.class_namespace}, nodes=[
                Xmlnode('arguments', nodes=[
                    Xmlnode('argument', attributes={'name': 'filesystem', 'xsi:type': 'object'}, node_text='Magento\\Framework\\Filesystem\\Driver\\File')
                ])
            ]),
            Xmlnode('type', attributes={'name': logger_class.class_namespace}, nodes=[
                Xmlnode('arguments', nodes=[
                    Xmlnode('argument', attributes={'name': 'name', 'xsi:type': 'string'}, node_text=logger_name),
                    Xmlnode('argument', attributes={'name': 'handlers', 'xsi:type': 'array'}, nodes=[
                        Xmlnode('item', attributes={'name': 'system', 'xsi:type': 'object'}, node_text=handler_class.class_namespace)
                    ])
                ])
            ])
        ])

        self.add_xml('etc/di.xml', di_xml)

        self.add_static_file(
            '.',
            Readme(
                specifications=" - Custom Logger\n\t- {} -> var/log/{}".format(logger_class.class_namespace, file_name),
            )
        )

    @classmethod
    def params(cls):
        return [
            SnippetParam(
                name='logger_name',
                required=True,
                description='Name of the logger (e.g. MyLogger)',
                regex_validator=r'^[a-zA-Z]\w*$',
                error_message='Only alphanumeric characters allowed, must start with a letter.'
            ),
            SnippetParam(
                name='file_name',
                required=True,
                default='custom.log',
                description='Log file name (e.g. my_module.log)',
                regex_validator=r'^[\w\.-]+$',
                error_message='Invalid filename.'
            )
        ]