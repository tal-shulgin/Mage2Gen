import os
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme

class RouterSnippet(Snippet):
    snippet_label = "Router"

    description = """
    Custom routers
    
    Create an implementation of RouterInterface to create a custom router, and define the match() function in this class to use your own route matching logic.

    If you need route configuration data, use the Route Config class.
    """

    def add(self, routername='', adminhtml=False, ajax=False, extra_params=None, top_level_menu=True):
        file_path = 'etc/{}/di.xml'.format('adminhtml' if adminhtml else 'frontend')
        
        # Create route class
        router_class_parts = ['Controller']
        if adminhtml:
            router_class_parts.append('Adminhtml')
        router_class_parts.append('Router')

        target_module = f"{self._module.package.lower()}_{self._module.name.lower()}"

        router = Phpclass('\\'.join(router_class_parts), implements=["RouterInterface"], dependencies=[
            'Magento\\Framework\\App\\Action\\Forward',
            'Magento\\Framework\\App\\ActionFactory',
            'Magento\\Framework\\App\\RequestInterface',
            'Magento\\Framework\\App\\RouterInterface',
        ], attributes=[
            'protected $actionFactory;'
        ])

        router.add_method(Phpmethod(
            '__construct',
            body="$this->actionFactory = $actionFactory;",
            params=[
                "ActionFactory $actionFactory"
            ],
            docstring=[
                'Router constructor',
                '',
                '@param ActionFactory $actionFactory',
            ]
        ))

        router.add_method(Phpmethod(
            'match',
            body=f"""
        $identifier = trim($request->getPathInfo(), '/');

        if (strpos($identifier, '{routername}') !== false) {{
            $request->setModuleName('{target_module}')
                ->setControllerName('index')
                ->setActionName('index');
            $request->setAlias(\\Magento\\Framework\\Url::REWRITE_REQUEST_PATH_ALIAS, $identifier);

            return $this->actionFactory->create(Forward::class);
        }}
        return null;
            """,
            params=[
                "RequestInterface $request"
            ],
            docstring=[
                '{@inheritdoc}',
            ]
        ))

        self.add_class(router)

        # Create config router
        module_node = Xmlnode('module', attributes={'name': self.module_name})
        if adminhtml:
            module_node.attributes['before'] = 'Magento_Backend'

        router_list_config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
            Xmlnode('type', attributes={'name': r'Magento\Framework\App\RouterList'}, nodes=[
                Xmlnode('arguments', nodes=[
                    Xmlnode('argument', attributes={'name': 'routerList', 'xsi:type': 'array'}, nodes=[
                        Xmlnode('item', attributes={'name': '{}'.format(routername), 'xsi:type': 'array'}, nodes=[
                            Xmlnode('item', attributes={'name': 'class', 'xsi:type': 'string'}, node_text=router.class_namespace),
                            Xmlnode('item', attributes={'name': 'disable', 'xsi:type': 'boolean'}, node_text="false"),
                            Xmlnode('item', attributes={'name': 'sortOrder', 'xsi:type': 'string'}, node_text="999"),
                        ])
                    ])
                ])
            ])
        ])
        self.add_xml(file_path, router_list_config)

    @classmethod
    def params(cls):
        return [
            SnippetParam(name='routername', required=False, description='On empty uses module name in lower case',
                regex_validator= r'^[a-z]{1}\w{2,}$',
                error_message='Only lowercase alphanumeric and underscore characters are allowed, and need to start with a alphabetic character. Minimum length is 3.',
                repeat=True),
            SnippetParam(name='adminhtml', yes_no=True),
        ]
