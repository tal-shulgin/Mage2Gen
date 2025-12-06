from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class CategoryAttributeSnippet(Snippet):
    snippet_label = 'Category Attribute'
    description = "Add an EAV attribute to Categories."

    def add(self, code=None, label=None, input_type='text', required=False, **kwargs):
        # Support legacy argument names
        if 'attribute_label' in kwargs and not label: label = kwargs['attribute_label']
        if 'frontend_input' in kwargs and not input_type: input_type = kwargs['frontend_input']

        if not code and label:
            code = label.lower().replace(" ", "_")

        package = self._module.package
        module = self._module.name
        class_name = f"Add{upperfirst(code)}CategoryAttribute"
        namespace = f"{package}\\{module}\\Setup\\Patch\\Data"

        content = TemplateEngine.render('snippets/attribute/patch.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'entity_type_const': "Magento\\Catalog\\Model\\Category::ENTITY",
            'attribute_code': code,
            'label': label,
            'type': 'varchar', # Simplified for example
            'input': input_type,
            'source': '',
            'frontend': '',
            'backend': '',
            'required': 'true' if required else 'false',
            'sort_order': 100,
            'scope': r'\Magento\Eav\Model\Entity\Attribute\ScopedAttributeInterface::SCOPE_STORE',
            'default': 'null',
            'searchable': 'false',
            'filterable': 'false',
            'comparable': 'false',
            'visible_on_front': 'false',
            'unique': 'false',
            'apply_to': ''
        })
        self.add_static_file(f"Setup/Patch/Data/{class_name}", StaticFile(f"{class_name}.php", body=content))
        
        # UI Component Form
        form_config = Xmlnode('form', attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'}, nodes=[
            Xmlnode('fieldset', attributes={'name': 'general'}, nodes=[
                Xmlnode('field', attributes={'name': code, 'formElement': 'input'}, nodes=[
                    Xmlnode('settings', nodes=[
                        Xmlnode('label', node_text=label),
                        Xmlnode('dataType', node_text='text')
                    ])
                ])
            ])
        ])
        self.add_xml('view/adminhtml/ui_component/category_form.xml', form_config)

        self.add_static_file('.', Readme(specifications=f" - Category Attribute: {code}"))