import unittest
import os

from mage2gen import Module
from mage2gen.snippets import CustomerAttributeSnippet
from tests import utils


class TestSnippetCustomerAttribute(unittest.TestCase):

    def test_snippet(self):
        module = Module(package='Package', name='Name', description='Description')
        snippet = CustomerAttributeSnippet(module)

        # The V3 snippet handles legacy arguments via **kwargs mapping
        sample_output = snippet.add(
            attribute_label='test',
            customer_forms='adminhtml_customer', 
            customer_entity='customer', 
            frontend_input='text',
            static_field=True, 
            required=False, 
            source_model='custom', 
            source_model_options='value1, value2, value3')

        result = utils.CodeSniffer.generate_and_test(module)
        self.assertTrue(result)

    def tearDown(self):
        utils.CodeSniffer.cleanup()