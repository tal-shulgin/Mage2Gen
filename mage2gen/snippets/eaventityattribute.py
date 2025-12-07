import os
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme
from ..utils import upperfirst
from ..core.template import TemplateEngine

class EavEntityAttributeSnippet(Snippet):
    snippet_label = 'EAV Attribute (custom)'

    FRONTEND_INPUT_TYPE = [
        ("text","Text Field"),
        ("textarea","Text Area"),
        ("date","Date"),
        ("boolean","Yes/No"),
        ("multiselect","Multiple Select"),
        ("select","Dropdown"),
        ("price","Price"),
        ("static","Static")
    ]

    FRONTEND_INPUT_VALUE_TYPE = {
        "text":"varchar",
        "textarea":"text",
        "date":"date",
        "boolean":"int",
        "multiselect":"varchar",
        "select":"int",
        "price":"decimal",
    }

    description = "Install Magento 2 custom eav entity attributes programmatically."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = 1

    def add(self, entity_model_class, attribute_label, frontend_input='text', required=False, options=None, source_model=False, extend_adminhtml_form=False, extra_params=None):
        entity_type = "{}::ENTITY".format(entity_model_class)
        entity_table = '{}_{}_entity'.format(self._module.package.lower(), entity_model_class.split('\\')[-1].lower())
        extra_params = extra_params if extra_params else {}

        self.count += 1
        value_type = self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input,'int')
        value_type = value_type if value_type != 'date' else 'datetime'
        user_defined = 'true'
        
        # Options logic
        options_list = options.split(',') if options else []
        options_array = [x.strip() for x in options_list] if not source_model else None

        attribute_code = extra_params.get('attribute_code', None)
        if not attribute_code:
            attribute_code = attribute_label.lower().replace(' ','_')[:60]

        split_attribute_code = attribute_code.split('_')
        attribute_code_capitalized = ''.join(upperfirst(item) for item in split_attribute_code)

        source_model_class = "''"
        if source_model and frontend_input in ['multiselect', 'select']:
            source_model_class = r"\{}\{}\Model\Attribute\Source\{}::class".format(self._module.package, self._module.name, attribute_code_capitalized)
            # Logic to add source model class
            options_php_array = '[\n' + ',\n'.join(["['value' => '" + val.lower() + "', 'label' => __('" + val + "')]" for val in options_list]) + '\n]'
            self.add_source_model(attribute_code_capitalized, options_php_array)

        # Generate Body using Jinja2
        methodBody = TemplateEngine.render('attributes/eavattribute.j2', {
            'entity_type': entity_type,
            'attribute_code': attribute_code,
            'attribute_label': attribute_label,
            'value_type': value_type,
            'frontend_input': frontend_input,
            'user_defined': user_defined,
            'required': 'true' if required else 'false',
            'options_array': options_array,
            'unique': 'true' if extra_params.get('unique', False) else 'false',
            'default': 'null',
            'backend': r'Magento\Eav\Model\Entity\Attribute\Backend\ArrayBackend' if frontend_input == 'multiselect' else '',
            'source_model': source_model_class,
            'sort_order': '30'
        })

        patchType = 'add'
        install_patch = Phpclass('Setup\\Patch\\Data\\{}{}{}Attribute'.format(patchType, attribute_code_capitalized, entity_model_class.split('\\')[-1]),
            implements=['DataPatchInterface', 'PatchRevertableInterface'],
            dependencies=[
                'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
                'Magento\\Framework\\Setup\\Patch\\PatchRevertableInterface',
                'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
                'Magento\\Eav\\Setup\\EavSetupFactory',
                'Magento\\Eav\\Setup\\EavSetup',
            ]
        )

        install_patch.add_method(Phpmethod(
            '__construct',
            params=['protected ModuleDataSetupInterface $moduleDataSetup', 'protected EavSetupFactory $eavSetupFactory'],
            body="",
            docstring=['Constructor']
        ))

        install_patch.add_method(Phpmethod(
            'apply',
            return_type='void',
            body_start='$this->moduleDataSetup->getConnection()->startSetup();',
            body_return='$this->moduleDataSetup->getConnection()->endSetup();',
            body="""/** @var EavSetup $eavSetup */
$eavSetup = $this->eavSetupFactory->create(['setup' => $this->moduleDataSetup]);
""" + methodBody,
            docstring=['{@inheritdoc}']
        ))

        install_patch.add_method(Phpmethod('revert', return_type='void', body=f"""$eavSetup = $this->eavSetupFactory->create(['setup' => $this->moduleDataSetup]);\n$eavSetup->removeAttribute(\\{entity_type}, '{attribute_code}');"""))
        install_patch.add_method(Phpmethod('getAliases', return_type='array', body='return [];'))
        install_patch.add_method(Phpmethod('getDependencies', access='public static', return_type='array', body='return [];'))

        self.add_class(install_patch)

        # Module Sequence
        etc_module = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
            Xmlnode('module', attributes={'name': self.module_name}, nodes=[
                Xmlnode('sequence', attributes={}, nodes=[Xmlnode('module', attributes={'name': 'Magento_Eav'})])
            ])
        ])
        self.add_xml('etc/module.xml', etc_module)

        # UI Component Form
        if extend_adminhtml_form:
            ui_form = Xmlnode('form', nodes=[
                Xmlnode('fieldset', attributes={'name': 'general'}, nodes=[
                    Xmlnode('field', attributes={'name': attribute_code, 'formElement': frontend_input, 'sortOrder': str(10 * self.count)}, nodes=[
                        Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
                            Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
                                Xmlnode('item', attributes={'name': 'source', 'xsi:type': 'string'}, node_text=attribute_code),
                            ]),
                        ]),
                        Xmlnode('settings', nodes=[
                            Xmlnode('dataType', node_text='text'),
                            Xmlnode('label', attributes={'translate': 'true'}, node_text=attribute_label),
                            Xmlnode('dataScope', node_text=attribute_code),
                            Xmlnode('validation', nodes=[
                                Xmlnode('rule', attributes={'name': 'required-entry', 'xsi:type': 'boolean'}, node_text='true' if required else 'false'),
                            ]),
                        ]),
                    ]),
                ]),
            ])
            self.add_xml('view/adminhtml/ui_component/{}_form.xml'.format(entity_table), ui_form)

        self.add_static_file('.', Readme(attributes=" - EAV (custom) - {} ({})".format(attribute_label, attribute_code)))

    def add_source_model(self, attribute_code_capitalized, options_php_array_string):
        source_model = Phpclass(r'Model\\Attribute\Source\\{}'.format(upperfirst(attribute_code_capitalized)),
            extends='\\Magento\\Eav\\Model\\Entity\\Attribute\\Source\\AbstractSource')

        source_model.add_method(Phpmethod(
            'getAllOptions',
            body="$this->_options = " + options_php_array_string + ";\n"
                 "return $this->_options;",
            docstring=['getAllOptions', '', '@return array']
        ))
        self.add_class(source_model)