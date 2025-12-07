import os
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme
from ..utils import upperfirst, lowerfirst
from ..schema import Table, Constraint, Index
from ..core.template import TemplateEngine
from ..types import get_php_type, get_php_doc_type

class InterfaceClass(Phpclass):
    """
    Overrides Phpclass to use the Interface template.
    """
    def generate(self):
        return TemplateEngine.render('interface.j2', self.context_data())

class InterfaceMethod(Phpmethod):
    """
    Overrides Phpmethod to use the Interface Method template.
    """
    def generate(self):
        return TemplateEngine.render('interface_method.j2', {
            'docstring': self.docstring_code(),
            'method': self.name,
            'params': self.params_code(),
            'return_type': self.return_type_code()
        }).replace('\t', '    ')

class EavEntitySnippet(Snippet):
    snippet_label = 'EAV Entity'
    description = """
    Create a custom EAV Entity with Model, Resource Model, Collection, Repositories, and API Interfaces.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = 0

    def add(self, entity_name, adminhtml_grid=False, adminhtml_form=False, web_api=False, extra_params=False):
        field_name = 'title'
        field_type = 'varchar'

        self.count += 1
        extra_params = extra_params if extra_params else {}

        entity_table = '{}_{}_entity'.format(self._module.package.lower(), entity_name.lower())
        entity_id = 'entity_id' # Standard ID for main table

        field_element_type = 'input'

        split_field_name = field_name.split('_')
        field_name_capitalized = ''.join(upperfirst(item) for item in split_field_name)

        split_entity_name = entity_name.split('_')
        entity_name_capitalized = ''.join(upperfirst(item) for item in split_entity_name)
        entity_name_capitalized_after = lowerfirst(entity_name_capitalized)

        split_entity_id = entity_id.split('_')
        entity_id_capitalized = ''.join(upperfirst(item) for item in split_entity_id)
        entity_id_capitalized_after = lowerfirst(entity_id_capitalized)

        collection_entity_class_name = "\\{}\\{}\\Model\\ResourceModel\\{}\\Collection".format(self._module.package,
            self._module.name,
            entity_name_capitalized.replace('_', '\\'),
        )

        extension_interface_class_name = "\\{}\\{}\\Api\\Data\\{}ExtensionInterface".format(self._module.package,
            self._module.name,
            entity_name_capitalized.replace('_', '\\')
        )

        top_level_menu = extra_params.get('top_level_menu', True)

        # ---------------------------------------------------------
        # Schema Generation
        # ---------------------------------------------------------
        
        tables = []

        # 1. Main Entity Table
        main_table = Table(entity_table, comment="{} Table".format(entity_table))
        main_table.add_column(entity_id, 'int', padding=10, unsigned=True, nullable=False, identity=True, comment="Entity Id")
        main_table.add_primary_key(entity_id)

        # Main Table Custom Column (e.g., 'title')
        col_attributes = {'nullable': True}
        if extra_params.get('unsigned'):
            col_attributes['unsigned'] = True
            col_attributes['length'] = '255'
        
        main_table.add_column(field_name, field_type, **col_attributes)
        tables.append(main_table)

        # 2. EAV Value Tables
        for eav_type in ['datetime', 'decimal', 'int', 'text', 'varchar']:
            eav_entity_type_table = "{}_{}".format(entity_table, eav_type)
            eav_entity_type_table_upper = eav_entity_type_table.upper()
            
            table = Table(eav_entity_type_table, comment="{} Table".format(eav_entity_type_table))
            
            # Standard Columns
            table.add_column('value_id', 'int', padding=11, unsigned=False, nullable=False, identity=True, comment="Value ID")
            table.add_column('attribute_id', 'smallint', padding=5, unsigned=True, nullable=False, default="0", comment="Attribute ID")
            table.add_column('entity_id', 'int', padding=10, unsigned=True, nullable=False, default="0", comment="Entity ID")
            
            # Value Column
            val_kwargs = {'nullable': eav_type != 'decimal', 'comment': 'Value'}
            val_db_type = eav_type
            
            if eav_type == 'datetime':
                val_kwargs['nullable'] = False
            elif eav_type == 'decimal':
                val_kwargs['scale'] = '4'
                val_kwargs['precision'] = '12'
                val_kwargs['unsigned'] = False
                val_kwargs['nullable'] = False
                val_kwargs['default'] = '0'
            elif eav_type == 'int':
                val_db_type = 'int'
                val_kwargs['padding'] = 11
                val_kwargs['unsigned'] = False
                val_kwargs['nullable'] = False
                val_kwargs['default'] = '0'
            elif eav_type == 'varchar':
                val_kwargs['length'] = '255'
            
            table.add_column('value', val_db_type, **val_kwargs)

            # Constraints
            table.add_primary_key('value_id')

            fk_attr = Constraint(Constraint.FOREIGN, 
                referenceId="{}_ATTRIBUTE_ID_EAV_ATTRIBUTE_ATTRIBUTE_ID".format(eav_entity_type_table_upper),
                table=eav_entity_type_table,
                column='attribute_id',
                referenceTable='eav_attribute',
                referenceColumn='attribute_id',
                onDelete='CASCADE'
            )
            fk_attr.add_column('attribute_id')
            table.add_constraint(fk_attr)

            fk_entity = Constraint(Constraint.FOREIGN,
                referenceId="{}_ENTITY_ID_{}_ENTITY_ID".format(eav_entity_type_table_upper, entity_table.upper()),
                table=eav_entity_type_table,
                column='entity_id',
                referenceTable=entity_table,
                referenceColumn=entity_id,
                onDelete='CASCADE'
            )
            fk_entity.add_column('entity_id')
            table.add_constraint(fk_entity)

            unique = Constraint(Constraint.UNIQUE,
                referenceId="{}_ENTITY_ID_ATTRIBUTE_ID".format(eav_entity_type_table_upper)
            )
            unique.add_column('entity_id')
            unique.add_column('attribute_id')
            table.add_constraint(unique)

            idx_attr = Index("{}_ATTRIBUTE_ID".format(eav_entity_type_table_upper))
            idx_attr.add_column('attribute_id')
            table.add_index(idx_attr)

            if eav_type != 'text':
                idx_val = Index("{}_ENTITY_ID_ATTRIBUTE_ID_VALUE".format(eav_entity_type_table_upper))
                idx_val.add_column('entity_id')
                idx_val.add_column('attribute_id')
                idx_val.add_column('value')
                table.add_index(idx_val)

            tables.append(table)

        # Generate the XML
        schema_nodes = [t.to_xml_node() for t in tables]
        self.add_xml('etc/db_schema.xml', Xmlnode('schema', 
            attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd"},
            nodes=schema_nodes
        ))

        # ---------------------------------------------------------
        # End Schema Generation
        # ---------------------------------------------------------

        # Create resource class
        resource_entity_class = Phpclass('Model\\ResourceModel\\' + entity_name_capitalized.replace('_', '\\'), extends='\\Magento\\Eav\\Model\\Entity\\AbstractEntity')
        resource_entity_class.add_method(Phpmethod('_construct',
            access=Phpmethod.PROTECTED,
            body="$this->setType('{}');".format(entity_table),
            docstring=['Define resource model', '', '@return void']))
        self.add_class(resource_entity_class)

        # Create api data interface class
        api_data_class = InterfaceClass('Api\\Data\\' + entity_name_capitalized.replace('_', '\\') + 'Interface',
            extends='\\Magento\\Framework\\Api\\ExtensibleDataInterface',
            attributes=[
                "const {} = '{}';".format(field_name.upper(),field_name),
                "const {} = '{}';".format(entity_id.upper(),entity_id)
            ])

        api_data_class.add_method(InterfaceMethod('get'+entity_id_capitalized,docstring=['Get {}'.format(entity_id),'@return {}'.format('string|null')], return_type='?string'))
        api_data_class.add_method(InterfaceMethod('set'+entity_id_capitalized,params=['${}'.format(entity_id_capitalized_after)],docstring=['Set {}'.format(entity_id),'@param string ${}'.format(entity_id_capitalized_after),'@return \\{}'.format(api_data_class.class_namespace)], return_type='\\{}'.format(api_data_class.class_namespace)))
        
        api_data_class.add_method(InterfaceMethod('get'+field_name_capitalized,docstring=['Get {}'.format(field_name),'@return {}'.format('string|null')], return_type='?string'))
        api_data_class.add_method(InterfaceMethod('set'+field_name_capitalized,params=['${}'.format(lowerfirst(field_name_capitalized))],docstring=['Set {}'.format(field_name),'@param string ${}'.format(lowerfirst(field_name_capitalized)),'@return \\{}'.format(api_data_class.class_namespace)], return_type='\\{}'.format(api_data_class.class_namespace)))
        
        api_data_class.add_method(InterfaceMethod('getExtensionAttributes', docstring=['Retrieve existing extension attributes object or create a new one.','@return ' + extension_interface_class_name + '|null'], return_type=extension_interface_class_name + '|null'))
        api_data_class.add_method(InterfaceMethod('setExtensionAttributes', params=[extension_interface_class_name + ' $extensionAttributes'], docstring=['Set an extension attributes object.','@param ' + extension_interface_class_name +' $extensionAttributes','@return $this'], return_type='self'))
        self.add_class(api_data_class)

        # Create api data search interface class
        api_data_search_class = InterfaceClass('Api\\Data\\' + entity_name_capitalized.replace('_', '\\') + 'SearchResultsInterface',extends=r'\Magento\Framework\Api\SearchResultsInterface')
        api_data_search_class.add_method(InterfaceMethod('getItems',docstring=['Get {} list.'.format(entity_name),'@return \\{}[]'.format(api_data_class.class_namespace)], return_type='\\{}[]'.format(api_data_class.class_namespace)))
        api_data_search_class.add_method(InterfaceMethod('setItems',params=['array $items'],docstring=['Set {} list.'.format(field_name),'@param \\{}[] $items'.format(api_data_class.class_namespace),'@return $this'], return_type='self'))
        self.add_class(api_data_search_class)

        # Create api repository interface class
        api_repository_class = InterfaceClass('Api\\' + entity_name_capitalized.replace('_', '\\') + 'RepositoryInterface',dependencies=[r'Magento\Framework\Api\SearchCriteriaInterface'])
        api_repository_class.add_method(InterfaceMethod('save',params=['\\{} ${}'.format(api_data_class.class_namespace,entity_name_capitalized_after)],docstring=['Save {}'.format(entity_name),'@param \\{} ${}'.format(api_data_class.class_namespace,entity_name_capitalized_after),'@return \\{}'.format(api_data_class.class_namespace),r'@throws \Magento\Framework\Exception\LocalizedException'], return_type='\\{}'.format(api_data_search_class.class_namespace)))
        api_repository_class.add_method(InterfaceMethod('get',params=['${}'.format(entity_id_capitalized_after)],docstring=['Retrieve {}'.format(entity_name),'@param string ${}'.format(entity_id_capitalized_after),'@return \\{}'.format(api_data_class.class_namespace),r'@throws \Magento\Framework\Exception\LocalizedException'], return_type='\\{}'.format(api_data_search_class.class_namespace)))
        api_repository_class.add_method(InterfaceMethod('getList',params= [r'\Magento\Framework\Api\SearchCriteriaInterface $searchCriteria'], docstring=['Retrieve {} matching the specified criteria.'.format(entity_name),r'@param \Magento\Framework\Api\SearchCriteriaInterface $searchCriteria','@return \\{}'.format(api_data_search_class.class_namespace),r'@throws \Magento\Framework\Exception\LocalizedException'], return_type='\\{}'.format(api_data_search_class.class_namespace)))
        api_repository_class.add_method(InterfaceMethod('delete',params=['\\{} ${}'.format(api_data_class.class_namespace,entity_name_capitalized_after)],docstring=['Delete {}'.format(entity_name),'@param \\{} ${}'.format(api_data_class.class_namespace,entity_name_capitalized_after),'@return bool true on success',r'@throws \Magento\Framework\Exception\LocalizedException'], return_type='bool'))
        api_repository_class.add_method(InterfaceMethod('deleteById',params=['${}'.format(entity_id_capitalized_after)],docstring=['Delete {} by ID'.format(entity_name),'@param string ${}'.format(entity_id_capitalized_after),'@return bool true on success','@throws \\Magento\\Framework\\Exception\\NoSuchEntityException','@throws \\Magento\\Framework\\Exception\\LocalizedException'], return_type='bool'))
        self.add_class(api_repository_class)

        # Create model class
        entity_class = Phpclass('Model\\' + entity_name_capitalized.replace('_', '\\'),
            dependencies=[
                api_data_class.class_namespace,
                api_data_class.class_namespace + 'Factory',
                'Magento\\Framework\\Api\\DataObjectHelper',
            ],
            extends='\\Magento\\Framework\\Model\\AbstractModel',
            attributes=[
                "const ENTITY = '{}';".format(entity_table),
                'protected ${}DataFactory;\n'.format(entity_name.lower()),
                'protected $_eventPrefix = \'{}\';'.format(entity_table),
            ])
            
        entity_class.add_method(Phpmethod('__construct', access=Phpmethod.PUBLIC,
            params=[
                r"\Magento\Framework\Model\Context $context",
                r"\Magento\Framework\Registry $registry",
                "DataObjectHelper $dataObjectHelper",
                "\\" + resource_entity_class.class_namespace + " $resource",
                collection_entity_class_name + " $resourceCollection",
                "{}InterfaceFactory ${}DataFactory".format(entity_name_capitalized, entity_name.lower()),
                "array $data = []",
            ],
            body="""parent::__construct($context, $registry, $resource, $resourceCollection, $data);
            $this->{variable}DataFactory = ${variable}DataFactory;
            $this->dataObjectHelper = $dataObjectHelper;
            """.format(variable=entity_name.lower()),
            docstring=['Constructor']
        ))

        entity_class.add_method(Phpmethod('getDataModel', access=Phpmethod.PUBLIC,
            body="""${variable}Data = $this->getData();
            
            ${variable}DataObject = $this->{variable}DataFactory->create();
            $this->dataObjectHelper->populateWithArray(
                ${variable}DataObject,
                ${variable}Data,
                {variable_upper}Interface::class
            );
            
            return ${variable}DataObject;
            """.format(variable=entity_name.lower(), variable_upper=entity_name_capitalized),
            return_type="{}Interface".format(entity_name_capitalized),
            docstring=['Get Data Model']
        ))
        self.add_class(entity_class)

        # Entity Setup
        entity_setup = Phpclass('Setup\\{}Setup'.format(entity_name_capitalized.replace('_', '\\')),
                                extends='EavSetup',
                                dependencies=['Magento\\Eav\\Setup\\EavSetup']
                                )

        entity_setup.add_method(
            Phpmethod('getDefaultEntities', return_type="array", body=r"""
                            return [\r
                                 \{entity_class}::ENTITY => [
                                    'entity_model' => \{resource_class}::class,
                                    'table' => '{entity_table}',
                                    'attributes' => [
                                        'title' => [
                                            'type' => 'static'
                                        ]
                                    ]
                                ]
                            ];""".format(entity_class=entity_class.class_namespace, entity_table=entity_table, resource_class=resource_entity_class.class_namespace))
        )
        self.add_class(entity_setup)

        # Install Patch
        install_patch = Phpclass(
            'Setup\\Patch\\Data\\Default{}Entity'.format(entity_name_capitalized.replace('_', '\\')),
            implements=['DataPatchInterface'],
            dependencies=[
                'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
                'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
                "{}Factory".format(entity_setup.class_namespace),
                entity_setup.class_namespace
            ],
            attributes=[
                "/**\n\t * @var {}Setup\n\t */\n\tprivate ${}SetupFactory;".format(entity_name_capitalized.replace('_', '\\'), lowerfirst(entity_name_capitalized.replace('_', '\\')))
            ]
            )

        install_patch.add_method(Phpmethod(
            '__construct',
            params=[
                'protected ModuleDataSetupInterface $moduleDataSetup',
                'protected {}SetupFactory ${}SetupFactory'.format(entity_name_capitalized.replace('_', '\\'), lowerfirst(entity_name_capitalized.replace('_', '\\')))
            ],
            body="$this->{variable}SetupFactory = ${variable}SetupFactory;".format(variable=lowerfirst(entity_name_capitalized.replace('_', '\\'))),
            docstring=['Constructor']
        ))

        install_patch.add_method(Phpmethod('apply',
            body_start='$this->moduleDataSetup->getConnection()->startSetup();',
            body_return='$this->moduleDataSetup->getConnection()->endSetup();',
            return_type='void',
            body="""/** @var {class_name}Setup $customerSetup */
${variable}Setup = $this->{variable}SetupFactory->create(['setup' => $this->moduleDataSetup]);
${variable}Setup->installEntities();
""".format(variable=lowerfirst(entity_name_capitalized.replace('_', '\\')), class_name=entity_name_capitalized.replace('_', '\\')),
            docstring=['{@inheritdoc}']))
            
        install_patch.add_method(Phpmethod('getAliases', body="return [];", return_type='array', docstring=['{@inheritdoc}']))
        install_patch.add_method(Phpmethod('getDependencies', access='public static', body="return [];", return_type='array', docstring=['{@inheritdoc}']))

        self.add_class(install_patch)

        # Module Sequence
        etc_module = Xmlnode('config', attributes={
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
            Xmlnode('module', attributes={'name': self.module_name}, nodes=[
                Xmlnode('sequence', attributes={}, nodes=[
                Xmlnode('module', attributes={'name': 'Magento_Eav'})
            ])
            ])
        ])
        self.add_xml('etc/module.xml', etc_module)
        
        # Create collection
        collection_entity_class = Phpclass(
            'Model\\ResourceModel\\' + entity_name_capitalized.replace('_', '\\') + '\\Collection',
            extends='\\Magento\\Eav\\Model\\Entity\\Collection\\AbstractCollection',
            attributes=[
                "/**\n\t * @inheritDoc\n\t */\n\tprotected $_idFieldName = '{}';".format(entity_id),
            ]
        )
        collection_entity_class.add_method(Phpmethod('_construct',
            access=Phpmethod.PROTECTED,
            body="""$this->_init(
    \\{}::class,
    \\{}::class
);""".format(
                entity_class.class_namespace ,resource_entity_class.class_namespace),
            docstring=['Define resource model']))
        self.add_class(collection_entity_class)

        # Repository Implementation (Using ModelSnippet templates)
        repo_class = f"{entity_name_capitalized}Repository"
        repo_ns = f"{self._module.package}\\{self._module.name}\\Model"
        
        content = TemplateEngine.render('snippets/model/repository.j2', {
            'namespace': repo_ns,
            'class_name': repo_class,
            'repository_interface': api_repository_class.class_namespace,
            'interface_namespace': api_data_class.namespace,
            'interface_name': api_data_class.class_name,
            'model_name': entity_name_capitalized,
            'resource_namespace': resource_entity_class.namespace,
            'resource_name': resource_entity_class.class_name,
            'collection_namespace': collection_entity_class.namespace,
            'collection_name': collection_entity_class.class_name,
            'var_name': entity_name_capitalized_after,
            'id_field': entity_id
        })
        self.add_static_file("Model", StaticFile(f"{repo_class}.php", body=content))
        
        # Preferences
        self.add_xml('etc/di.xml', Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
            Xmlnode('preference', attributes={
                'for': api_repository_class.class_namespace,
                'type': f"{repo_ns}\\{repo_class}"
            }),
            Xmlnode('preference', attributes={
                'for': api_data_class.class_namespace,
                'type': entity_class.class_namespace # In EAV, Model usually implements Data interface
            }),
            Xmlnode('preference', attributes={
                'for': api_data_search_class.class_namespace,
                'type': r'Magento\Framework\Api\SearchResults'
            })
        ]))

        # --- ADMIN GRID / FORM LOGIC ---
        # Note: EAV grids are tricky because standard Magento UI components work best with Flat tables.
        # For EAV, the Collection must implement SearchResultInterface or use a grid aggregator.
        # We will generate standard UI components assuming the Collection can load data.
        
        if adminhtml_grid:
            self.add_adminhtml_grid(entity_name, entity_table, entity_id)

        if adminhtml_form:
            self.add_adminhtml_form(entity_name, entity_table, entity_id)
            self.add_acl(entity_name)

        if web_api:
            self.add_web_api(entity_name, entity_id)

        if web_api or adminhtml_form or adminhtml_grid:
            self.add_acl(entity_name)

        self.add_static_file(
            '.',
            Readme(
                specifications=" - Eav Entity\n\t- {}".format(entity_name),
            )
        )

    def add_adminhtml_grid(self, entity_name, entity_table, entity_id):
        route_id = f"{self._module.package.lower()}_{self._module.name.lower()}"
        model_lower = entity_name.lower()
        
        # Menu
        menu_xml = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Backend:etc/menu.xsd"}, nodes=[
            Xmlnode('menu', nodes=[
                Xmlnode('add', attributes={
                    'id': f"{self._module.package}::top_level",
                    'title': self._module.package,
                    'module': self.module_name,
                    'sortOrder': '99',
                    'resource': 'Magento_Backend::content'
                }),
                Xmlnode('add', attributes={
                    'id': f"{self._module.package}::{entity_table}",
                    'title': entity_name,
                    'module': self.module_name,
                    'sortOrder': '10',
                    'resource': f"{self.module_name}::{entity_name}",
                    'parent': f"{self._module.package}::top_level",
                    'action': f"{route_id}/{model_lower}/index"
                })
            ])
        ])
        self.add_xml('etc/adminhtml/menu.xml', menu_xml)
        
        # Layout
        layout_content = TemplateEngine.render('snippets/model/layout.j2', {
            'ui_component': f"{entity_table}_listing"
        })
        self.add_static_file(f"view/adminhtml/layout", StaticFile(f"{route_id}_{model_lower}_index.xml", body=layout_content))

        # Listing XML (Reuse Model Listing Template)
        # Note: We only have 'title' field by default in EAV entity
        fields = [{'name': 'title'}]
        
        listing_xml = TemplateEngine.render('snippets/model/listing.j2', {
            'table_name': entity_table,
            'model_name': upperfirst(entity_name),
            'id_field': entity_id,
            'fields': fields,
            'package': self._module.package,
            'module': self._module.name,
            'route_id': route_id,
            'model_lower': model_lower
        })
        self.add_static_file(f"view/adminhtml/ui_component", StaticFile(f"{entity_table}_listing.xml", body=listing_xml))
        
        # Page Actions Column
        actions_name = f"{upperfirst(entity_name)}Actions"
        actions_ns = f"{self._module.package}\\{self._module.name}\\Ui\\Component\\Listing\\Column"
        actions_content = TemplateEngine.render('snippets/model/actions.j2', {
            'namespace': actions_ns,
            'class_name': actions_name,
            'id_field': entity_id,
            'route_id': route_id,
            'model_lower': model_lower
        })
        self.add_static_file(f"Ui/Component/Listing/Column", StaticFile(f"{actions_name}.php", body=actions_content))
        
        # Data Provider
        dp_name = "DataProvider"
        dp_ns = f"{self._module.package}\\{self._module.name}\\Model\\{upperfirst(entity_name)}"
        # Note: Collection class name logic needs to be consistent
        coll_cls = f"{self._module.package}\\{self._module.name}\\Model\\ResourceModel\\{upperfirst(entity_name)}\\Collection"
        
        dp_content = TemplateEngine.render('snippets/model/dataprovider.j2', {
            'namespace': dp_ns,
            'collection_class': coll_cls,
            'register_key': entity_table
        })
        self.add_static_file(f"Model/{upperfirst(entity_name)}", StaticFile(f"{dp_name}.php", body=dp_content))

    def add_adminhtml_form(self, entity_name, entity_table, entity_id):
        route_id = f"{self._module.package.lower()}_{self._module.name.lower()}"
        model_lower = entity_name.lower()
        
        # Layouts
        layout_content = TemplateEngine.render('snippets/model/layout.j2', {
            'ui_component': f"{entity_table}_form"
        })
        self.add_static_file(f"view/adminhtml/layout", StaticFile(f"{route_id}_{model_lower}_edit.xml", body=layout_content))
        
        layout_new = f"""<?xml version="1.0"?>
<page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="urn:magento:framework:View/Layout/etc/page_configuration.xsd">
    <update handle="{route_id}_{model_lower}_edit"/>
</page>"""
        self.add_static_file(f"view/adminhtml/layout", StaticFile(f"{route_id}_{model_lower}_new.xml", body=layout_new))

        # Form XML
        fields = [{'name': 'title'}]
        form_xml = TemplateEngine.render('snippets/model/form.j2', {
            'table_name': entity_table,
            'model_name': upperfirst(entity_name),
            'id_field': entity_id,
            'fields': fields,
            'package': self._module.package,
            'module': self._module.name
        })
        self.add_static_file(f"view/adminhtml/ui_component", StaticFile(f"{entity_table}_form.xml", body=form_xml))

    def add_web_api(self, entity_name, entity_id):
        repo_interface = f"{self._module.package}\\{self._module.name}\\Api\\{upperfirst(entity_name)}RepositoryInterface"
        
        webapi_xml = Xmlnode('routes', attributes={
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Webapi:etc/webapi.xsd"
        }, nodes=[
            Xmlnode('route', attributes={'url': f"/V1/{entity_name.lower()}/:id", 'method': 'GET'}, nodes=[
                Xmlnode('service', attributes={'class': repo_interface, 'method': 'get'}),
                Xmlnode('resources', nodes=[Xmlnode('resource', attributes={'ref': 'anonymous'})])
            ]),
            Xmlnode('route', attributes={'url': f"/V1/{entity_name.lower()}", 'method': 'POST'}, nodes=[
                Xmlnode('service', attributes={'class': repo_interface, 'method': 'save'}),
                Xmlnode('resources', nodes=[Xmlnode('resource', attributes={'ref': 'anonymous'})])
            ]),
            Xmlnode('route', attributes={'url': f"/V1/{entity_name.lower()}/:id", 'method': 'DELETE'}, nodes=[
                Xmlnode('service', attributes={'class': repo_interface, 'method': 'deleteById'}),
                Xmlnode('resources', nodes=[Xmlnode('resource', attributes={'ref': 'anonymous'})])
            ])
        ])
        self.add_xml('etc/webapi.xml', webapi_xml)

    def add_acl(self, entity_name):
        acl_xml = Xmlnode('config', attributes={
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Acl/etc/acl.xsd"
        }, nodes=[
            Xmlnode('acl', nodes=[
                Xmlnode('resources', nodes=[
                    Xmlnode('resource', attributes={'id': 'Magento_Backend::admin'}, nodes=[
                        Xmlnode('resource', attributes={'id': 'Magento_Backend::stores'}, nodes=[
                            Xmlnode('resource', attributes={'id': 'Magento_Backend::stores_settings'}, nodes=[
                                Xmlnode('resource', attributes={'id': 'Magento_Config::config'}, nodes=[
                                    Xmlnode('resource', attributes={
                                        'id': f"{self.module_name}::{entity_name.lower()}",
                                        'title': entity_name
                                    })
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ])
        self.add_xml('etc/acl.xml', acl_xml)

    @classmethod
    def params(cls):
        return [
            SnippetParam(
                name='entity_name',
                description='Example: Blog',
                required=True,
                regex_validator= r'^[a-zA-Z]{1}\w+$',
                error_message='Only alphanumeric and underscore characters are allowed.',
                repeat=True
            ),
            SnippetParam(name='adminhtml_grid', yes_no=True),
            SnippetParam(name='adminhtml_form', yes_no=True),
            SnippetParam(name='web_api', yes_no=True),
        ]

    @classmethod
    def extra_params(cls):
        return [
            SnippetParam(
                name='top_level_menu',
                yes_no=True,
                default=True,
                repeat=True
            ),
        ]