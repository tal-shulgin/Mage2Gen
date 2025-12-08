from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst, to_pascal_case
from ..schema import Table, Column

class CustomerAttributeSnippet(Snippet):
    snippet_label = 'Customer Attribute'
    description = "Add an EAV attribute to Customers."

    def add(self, 
        code=None, 
        label=None, 
        input_type='text', 
        static_field=False,
        checkout_billing=False,
        checkout_shipping=False,
        **kwargs
    ):
        # Support legacy argument names
        if 'attribute_label' in kwargs and not label: label = kwargs['attribute_label']
        if 'frontend_input' in kwargs and not input_type: input_type = kwargs['frontend_input']

        if not code and label:
            code = label.lower().replace(" ", "_")

        package = self._module.package
        module = self._module.name
        class_name = f"Add{to_pascal_case(code)}CustomerAttribute"
        namespace = f"{package}\\{module}\\Setup\\Patch\\Data"

        # Forms Logic
        forms = ['adminhtml_customer']
        if kwargs.get('customer_forms'):
            # If passed as string "a,b,c" or list
            f_arg = kwargs['customer_forms']
            if isinstance(f_arg, str):
                forms = f_arg.split(',')
            else:
                forms = f_arg
        
        # PHP array string for template
        forms_php = ", ".join([f"'{f.strip()}'" for f in forms])

        # Type logic
        attr_type = 'static' if static_field else 'varchar'
        if input_type in ['int', 'boolean', 'select']:
            attr_type = 'int' if not static_field else 'int' # Simplification
        
        # 1. Generate Data Patch
        content = TemplateEngine.render('snippets/attribute/patch.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'entity_type_const': "Magento\\Customer\\Model\\Customer::ENTITY",
            'attribute_code': code,
            'label': label,
            'type': attr_type,
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
            'apply_to': '',
            'option': '[]',
            # We inject extra options for customer attributes
            'extra_options': f"'used_in_forms' => [{forms_php}], 'system' => 0" 
        })
        self.add_static_file(f"Setup/Patch/Data/{class_name}", StaticFile(f"{class_name}.php", body=content))

        # 2. Static Field Schema (db_schema.xml)
        if static_field:
            # We need to add a column to customer_entity
            # Note: In real scenarios, merging db_schema is complex. 
            # Here we generate a schema node. If one exists, Module.add_xml handles node merging.
            
            # Map input type to DB type
            db_type = 'varchar'
            if input_type in ['boolean', 'int', 'select']:
                db_type = 'int'
            
            col_attributes = {
                'name': code,
                'xsi:type': db_type,
                'nullable': 'true',
                'comment': label
            }
            if db_type == 'varchar':
                col_attributes['length'] = '255'

            schema_node = Xmlnode('schema', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd"}, nodes=[
                Xmlnode('table', attributes={'name': 'customer_entity'}, nodes=[
                    Xmlnode('column', attributes=col_attributes)
                ])
            ])
            self.add_xml('etc/db_schema.xml', schema_node)

        # 3. Checkout Integration (fieldset.xml)
        if checkout_billing or checkout_shipping:
            fieldset_content = TemplateEngine.render('snippets/customer/fieldset.j2', {
                'code': code,
                'checkout_billing': checkout_billing,
                'checkout_shipping': checkout_shipping
            })
            
            # We use StaticFile for simplicity here, but robustly we should use Xmlnode.
            # Using Xmlnode ensures we don't overwrite if multiple attributes add fields.
            
            billing_node = None
            shipping_node = None
            
            if checkout_billing:
                billing_node = Xmlnode('fieldset', attributes={'id': 'extra_checkout_billing_address_fields'}, nodes=[
                    Xmlnode('field', attributes={'name': code}, nodes=[
                        Xmlnode('aspect', attributes={'name': 'to_order_address'}),
                        Xmlnode('aspect', attributes={'name': 'to_customer_address'})
                    ])
                ])
                
            if checkout_shipping:
                shipping_node = Xmlnode('fieldset', attributes={'id': 'extra_checkout_shipping_address_fields'}, nodes=[
                    Xmlnode('field', attributes={'name': code}, nodes=[
                        Xmlnode('aspect', attributes={'name': 'to_order_address'}),
                        Xmlnode('aspect', attributes={'name': 'to_customer_address'})
                    ])
                ])
            
            fieldset_nodes = []
            if billing_node: fieldset_nodes.append(billing_node)
            if shipping_node: fieldset_nodes.append(shipping_node)
            
            fieldset_xml = Xmlnode('config', attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsi:noNamespaceSchemaLocation': "urn:magento:framework:DataObject/etc/fieldset.xsd"}, nodes=[
                Xmlnode('scope', attributes={'id': 'global'}, nodes=fieldset_nodes)
            ])
            
            self.add_xml('etc/fieldset.xml', fieldset_xml)

        self.add_static_file('.', Readme(specifications=f" - Customer Attribute: {code}"))