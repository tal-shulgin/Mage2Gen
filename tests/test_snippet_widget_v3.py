import unittest
from mage2gen import Module
from mage2gen.snippets import WidgetSnippet
from tests import utils

class TestSnippetWidgetV3(unittest.TestCase):

    def test_widget_generation(self):
        module = Module(package='Test', name='Module', description='Desc')
        snippet = WidgetSnippet(module)
        
        # Add widget
        snippet.add(
            name='PromotionalBanner',
            field='banner_text',
            field_type='text',
            sortorder=10
        )

        result = utils.CodeSniffer.generate_and_test(module)
        self.assertTrue(result)
        
        # Verify Block Class
        files = list(module._static_files.keys())
        self.assertTrue(any('PromotionalBanner.php' in f for f in files))
        
        # Verify Template
        self.assertTrue(any('promotionalbanner.phtml' in f for f in files))
        
        # Verify XML
        xmls = list(module._xmls.keys())
        self.assertTrue('etc/widget.xml' in xmls)

    def tearDown(self):
        utils.CodeSniffer.cleanup()