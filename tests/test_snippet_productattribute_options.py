import unittest
from mage2gen import Module
from mage2gen.snippets import ProductAttributeSnippet
from tests import utils

class TestSnippetProductAttributeOptions(unittest.TestCase):

    def test_options_generation(self):
        module = Module(package='Test', name='Module', description='Desc')
        snippet = ProductAttributeSnippet(module)
        
        # Add attribute with options
        snippet.add(
            code='color', 
            label='Color', 
            input_type='select', 
            options='Red,Green,Blue'
        )

        result = utils.CodeSniffer.generate_and_test(module)
        self.assertTrue(result)
        
        # Check for Source Model file
        # Key in _static_files matches the path passed to add_static_file
        # which is "Model/Config/Source/ColorOptions.php" joined with filename "ColorOptions.php" 
        # Wait, my add_static_file logic in snippet:
        # self.add_static_file(f"Model/Config/Source/{source_class_name}.php", ...
        # This might result in double filename if not careful.
        # Let's check internal dictionary keys.
        
        files = list(module._static_files.keys())
        has_source = any('ColorOptions.php' in f for f in files)
        self.assertTrue(has_source, f"Source Model not found in: {files}")

    def tearDown(self):
        utils.CodeSniffer.cleanup()