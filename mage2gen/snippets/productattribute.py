from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class ProductAttributeSnippet(Snippet):
    snippet_label = 'Product Attribute'
    description = "Add an EAV attribute to Products."

    def add(self, code=None, label=None, input_type='text', source_model='', required=False, sort_order=100, options=None, **kwargs):
        # Support legacy argument names
        if 'attribute_label' in kwargs and not label: label = kwargs['attribute_label']
        if 'frontend_input' in kwargs and not input_type: input_type = kwargs['frontend_input']
        
        if not code and label:
            code = label.lower().replace(" ", "_")
            
        package = self._module.package
        module = self._module.name
        
        class_name = f"Add{upperfirst(code)}ProductAttribute"
        namespace = f"{package}\\{module}\\Setup\\Patch\\Data"
        
        # Determine Type
        type_map = {'text': 'varchar', 'textarea': 'text', 'boolean': 'int', 'select': 'int', 'multiselect': 'varchar'}
        backend_type = type_map.get(input_type, 'varchar')
        
        source = source_model
        
        # Logic: Custom Source Model generation
        if input_type in ['select', 'multiselect']:
            if options:
                # Generate a custom source model
                source_class_name = f"{upperfirst(code)}Options"
                source_ns = f"{package}\\{module}\\Model\\Config\\Source"
                source = f"{source_ns}\\{source_class_name}"
                
                # Parse options string "Red, Green, Blue" -> [{'value':'red', 'label':'Red'}, ...]
                opts_list = []
                for opt in options.split(','):
                    opt = opt.strip()
                    opts_list.append({'value': opt.lower(), 'label': opt})
                
                source_content = TemplateEngine.render('snippets/attribute/source_model.j2', {
                    'namespace': source_ns,
                    'class_name': source_class_name,
                    'options': opts_list
                })
                
                self.add_static_file(f"Model/Config/Source/{source_class_name}", StaticFile(f"{source_class_name}.php", body=source_content))
                
            elif not source:
                # Default to Table if no options and no source provided
                source = "Magento\\Eav\\Model\\Entity\\Attribute\\Source\\Table"
        
        elif input_type == 'boolean':
            source = "Magento\\Eav\\Model\\Entity\\Attribute\\Source\\Boolean"
            
        backend = ""
        if input_type == 'multiselect':
            backend = "Magento\\Eav\\Model\\Entity\\Attribute\\Backend\\ArrayBackend"

        content = TemplateEngine.render('snippets/attribute/patch.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'entity_type_const': "Magento\\Catalog\\Model\\Product::ENTITY",
            'attribute_code': code,
            'label': label,
            'type': backend_type,
            'input': input_type,
            'source': source,
            'frontend': '',
            'backend': backend,
            'required': 'true' if required else 'false',
            'sort_order': sort_order,
            'scope': r'\Magento\Eav\Model\Entity\Attribute\ScopedAttributeInterface::SCOPE_GLOBAL',
            'default': 'null',
            'searchable': 'false',
            'filterable': 'false',
            'comparable': 'false',
            'visible_on_front': 'false',
            'unique': 'false',
            'apply_to': ''
        })
        
        self.add_static_file("Setup/Patch/Data", StaticFile(f"{class_name}.php", body=content))
        
        # Add Module Sequence
        config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
            Xmlnode('module', attributes={'name': f"{package}_{module}"}, nodes=[
                Xmlnode('sequence', attributes={}, nodes=[
                    Xmlnode('module', attributes={'name': 'Magento_Catalog'})
                ])
            ])
        ])
        self.add_xml('etc/module.xml', config)

        self.add_static_file('.', Readme(specifications=f" - Product Attribute: {code}"))