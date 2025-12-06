import unittest
from mage2gen import Module
from mage2gen.snippets import CustomerAttributeSnippet
from tests import utils

class TestSnippetCustomerAttributeAdvanced(unittest.TestCase):

    def test_checkout_integration(self):
        module = Module(package='Test', name='Module', description='Desc')
        snippet = CustomerAttributeSnippet(module)
        
        # Add attribute with checkout integration and static storage
        snippet.add(
            code='loyalty_number',
            label='Loyalty Number',
            static_field=True,
            checkout_billing=True,
            checkout_shipping=False
        )

        result = utils.CodeSniffer.generate_and_test(module)
        self.assertTrue(result)
        
        # Check for fieldset.xml
        xml_files = module._xmls.keys()
        self.assertTrue('etc/fieldset.xml' in xml_files)
        
        # Check for db_schema.xml (static field)
        self.assertTrue('etc/db_schema.xml' in xml_files)

    def tearDown(self):
        utils.CodeSniffer.cleanup()