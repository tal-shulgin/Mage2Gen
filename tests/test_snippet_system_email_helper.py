import unittest
from mage2gen import Module
from mage2gen.snippets import SystemSnippet
from tests import utils

class TestSnippetSystemEmailHelper(unittest.TestCase):

    def test_email_helper_generation(self):
        module = Module(package='Test', name='Module', description='Desc')
        snippet = SystemSnippet(module)
        
        # Add email field
        snippet.add(
            tab='general',
            section='contact',
            group='email',
            field='notification',
            field_type='email'
        )

        result = utils.CodeSniffer.generate_and_test(module)
        self.assertTrue(result)
        
        # Check for Helper file
        files = list(module._static_files.keys())
        # The key path depends on how add_static_file joined it
        # Expected: Helper/NotificationMail.php
        has_helper = any('NotificationMail.php' in f for f in files)
        self.assertTrue(has_helper, f"Helper not found in: {files}")

    def tearDown(self):
        utils.CodeSniffer.cleanup()