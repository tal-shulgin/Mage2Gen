from .. import Snippet, StaticFile, Readme, Xmlnode, Phpclass, Phpmethod
from ..core.template import TemplateEngine
from ..utils import upperfirst

class ProductTypeSnippet(Snippet):
    snippet_label = 'Product Type'
    description = "Create a custom Product Type."

    STATIC_PRODUCT_TYPES_SOURCE_MODELS = {
        'default': '\\Magento\\Catalog\\Model\\Product\\Type\\AbstractType',
        'simple': '\\Magento\\Catalog\\Model\\Product\\Type\\Simple',
        'virtual': '\\Magento\\Catalog\\Model\\Product\\Type\\Virtual',
        'configurable': '\\Magento\\ConfigurableProduct\\Model\\Product\\Type\\Configurable',
        'grouped': '\\Magento\\GroupedProduct\\Model\\Product\\Type\\Grouped',
        'downloadable': '\\Magento\\Downloadable\\Model\\Product\\Type',
        'bundle': '\\Magento\\Bundle\\Model\\Product\\Type',
        'giftcard': '\\Magento\\GiftCard\\Model\\Catalog\\Product\\Type\\Giftcard'
    }

    def add(self, code, label, extend_type='default', use_qty=True, extra_params=None):
        package = self._module.package
        module = self._module.name
        
        type_code = code.lower().replace(' ', '_')
        class_name = upperfirst(type_code)
        
        parent_class = self.STATIC_PRODUCT_TYPES_SOURCE_MODELS.get(extend_type, '\\Magento\\Catalog\\Model\\Product\\Type\\AbstractType')
        
        # 1. Product Type Model
        product_type_class = Phpclass(f"Model\\Product\\Type\\{class_name}", extends=parent_class, attributes=[
            f"const TYPE_ID = '{type_code}';"
        ])
        
        # Add methods via template or manually
        methods_body = TemplateEngine.render('snippets/producttype/methods.j2', {
            'class_name': class_name,
            'type_code': type_code
        })
        product_type_class.add_method(Phpmethod('deleteTypeSpecificData', body=methods_body, raw_body=True))
        
        self.add_class(product_type_class)
        
        # 2. Product Types XML
        xml_config = Xmlnode('config', attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Catalog:etc/product_types.xsd"}, nodes=[
            Xmlnode('type', attributes={
                'name': type_code,
                'label': label,
                'modelInstance': product_type_class.class_namespace,
                'isQty': 'true' if use_qty else 'false'
            })
        ])
        self.add_xml('etc/product_types.xml', xml_config)

        # 3. Data Patch (Registration)
        patch_name = f"Create{class_name}ProductType"
        patch_class = Phpclass(f"Setup\\Patch\\Data\\{patch_name}", implements=['DataPatchInterface'], dependencies=[
            'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
            'Magento\\Eav\\Setup\\EavSetup',
            'Magento\\Eav\\Setup\\EavSetupFactory',
            'Magento\\Framework\\Setup\\ModuleDataSetupInterface'
        ], attributes=[
            'private $moduleDataSetup;',
            'private $eavSetupFactory;'
        ])
        
        patch_class.add_method(Phpmethod('__construct', params=['ModuleDataSetupInterface $moduleDataSetup', 'EavSetupFactory $eavSetupFactory'], body='$this->moduleDataSetup = $moduleDataSetup;\n$this->eavSetupFactory = $eavSetupFactory;'))
        
        # Apply Body
        apply_body = f"""$this->moduleDataSetup->getConnection()->startSetup();
$eavSetup = $this->eavSetupFactory->create(['setup' => $this->moduleDataSetup]);

$fieldList = [
    'price',
    'special_price',
    'special_from_date',
    'special_to_date',
    'minimal_price',
    'cost',
    'tier_price',
    'weight',
];

foreach ($fieldList as $field) {{
    $applyTo = explode(
        ',',
        $eavSetup->getAttribute(\Magento\Catalog\Model\Product::ENTITY, $field, 'apply_to')
    );
    if (!in_array('{type_code}', $applyTo)) {{
        $applyTo[] = '{type_code}';
        $eavSetup->updateAttribute(
            \Magento\Catalog\Model\Product::ENTITY,
            $field,
            'apply_to',
            implode(',', $applyTo)
        );
    }}
}}

$this->moduleDataSetup->getConnection()->endSetup();"""

        patch_class.add_method(Phpmethod('apply', body=apply_body, return_type='void'))
        patch_class.add_method(Phpmethod('getDependencies', access='public static', body='return [];', return_type='array'))
        patch_class.add_method(Phpmethod('getAliases', body='return [];', return_type='array'))
        
        self.add_class(patch_class)

        self.add_static_file('.', Readme(specifications=f" - Product Type: {type_code}"))
