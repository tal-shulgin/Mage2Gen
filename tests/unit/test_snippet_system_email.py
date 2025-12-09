import unittest
from mage2gen import Module
from mage2gen.snippets import SystemSnippet
from tests import utils

class TestSnippetSystemEmail(unittest.TestCase):

    def test_email_generation(self):
        module = Module(package='Test', name='Module', description='Desc')
        snippet = SystemSnippet(module)
        
        # Add email field
        snippet.add(
            tab='general',
            section='contact',
            group='email',
            field='template',
            field_type='email',
            default_value='test_module_contact_email_template'
        )

        result = utils.CodeSniffer.generate_and_test(module)
        self.assertTrue(result)
        
        # Verify XML registration
        xml_files = module._xmls.keys()
        self.assertTrue('etc/email_templates.xml' in xml_files)
        
        # Verify HTML template
        static_files = module._static_files.keys()
        self.assertTrue(any('template.html' in f for f in static_files))

    def tearDown(self):
        utils.CodeSniffer.cleanup()