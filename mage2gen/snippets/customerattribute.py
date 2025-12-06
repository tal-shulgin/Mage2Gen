from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class CustomerAttributeSnippet(Snippet):
    snippet_label = 'Customer Attribute'
    description = "Add an EAV attribute to Customers."

    def add(self, code=None, label=None, input_type='text', **kwargs):
        # Support legacy argument names
        if 'attribute_label' in kwargs and not label: label = kwargs['attribute_label']
        if 'frontend_input' in kwargs and not input_type: input_type = kwargs['frontend_input']

        if not code and label:
            code = label.lower().replace(" ", "_")

        package = self._module.package
        module = self._module.name
        class_name = f"Add{upperfirst(code)}CustomerAttribute"
        namespace = f"{package}\\{module}\\Setup\\Patch\\Data"

        content = TemplateEngine.render('snippets/attribute/patch.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'entity_type_const': "Magento\\Customer\\Model\\Customer::ENTITY",
            'attribute_code': code,
            'label': label,
            'type': 'varchar',
            'input': input_type,
            'source': '',
            'frontend': '',
            'backend': '',
            'required': 'false',
            'sort_order': 100,
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
        self.add_static_file('.', Readme(specifications=f" - Customer Attribute: {code}"))