import unittest
import tempfile
import shutil
import os
from mage2gen import Module
from mage2gen.snippets import SystemSnippet
from tests import utils

class TestSnippetSystemAdvanced(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for file generation
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Cleanup temp directory
        shutil.rmtree(self.test_dir)
        utils.CodeSniffer.cleanup()

    def test_advanced_fields(self):
        module = Module(package='Test', name='Adv', description='Desc')
        snippet = SystemSnippet(module)
        
        # 1. Color Picker (Rich Type)
        snippet.add(
            tab='general', 
            section='ui', 
            group='design', 
            field='main_color', 
            type='color'
        )
        
        # 2. Image Upload with Dependency (Rich Type + Logic)
        snippet.add(
            tab='general', 
            section='ui', 
            group='design', 
            field='logo_upload', 
            type='image',
            depends='main_color:1'
        )

        # 3. Secure API Key (Security + Scope + Validation + Comment)
        snippet.add(
            tab='general',
            section='api',
            group='credentials',
            field='secret_key',
            type='text',          # Will become obscure due to encrypt=True
            scope='global',       # Restricted scope (showInWebsite=0, etc.)
            validate='required,no-empty', # Should map to classes
            comment='Keep this secret',
            encrypt=True
        )

        # Basic Syntax Check via CodeSniffer (Mocked or Real)
        result = utils.CodeSniffer.generate_and_test(module)
        self.assertTrue(result)
        
        # --- Robust Verification via File Generation ---
        
        # Generate files to the temp directory
        module.generate_module(self.test_dir)
        
        # Verify Static Files (PHP Classes) exist on disk
        # Path: {tmp}/{Package}/{Module}/...
        base_path = os.path.join(self.test_dir, 'Test', 'Adv')
        
        color_block = os.path.join(base_path, 'Block', 'Adminhtml', 'System', 'Config', 'Field', 'MainColorColor.php')
        self.assertTrue(os.path.exists(color_block), "Color Picker Block not generated on disk")
        
        image_backend = os.path.join(base_path, 'Model', 'Config', 'Backend', 'LogoUploadImage.php')
        self.assertTrue(os.path.exists(image_backend), "Image Backend Model not generated on disk")

        # Verify XML Content
        system_xml_path = os.path.join(base_path, 'etc', 'adminhtml', 'system.xml')
        self.assertTrue(os.path.exists(system_xml_path), "system.xml not generated")
        
        with open(system_xml_path, 'r') as f:
            xml_content = f.read()
            
        # Check Scope (Global = 1,0,0)
        self.assertIn('showInDefault="1"', xml_content)
        self.assertIn('showInWebsite="0"', xml_content)
        self.assertIn('showInStore="0"', xml_content)
        
        # Check Encryption
        self.assertIn('type="obscure"', xml_content)
        self.assertIn('Magento\\Config\\Model\\Config\\Backend\\Encrypted', xml_content)
        
        # Check Validation Mapping
        # 'required' -> 'required-entry', 'no-empty' -> 'no-whitespace'
        self.assertIn('required-entry', xml_content)
        self.assertIn('no-whitespace', xml_content)
        
        # Check Comment
        self.assertIn('Keep this secret', xml_content)
        
        # Check Dependency
        self.assertIn('<depends>', xml_content)
        self.assertIn('<field id="main_color">1</field>', xml_content)