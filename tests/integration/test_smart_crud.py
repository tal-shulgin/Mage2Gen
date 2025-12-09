import unittest
from tests.integration.base import IntegrationTestBase
from mage2gen.snippets.model import ModelSnippet

class TestSmartCrud(IntegrationTestBase):
    """
    Replaces verify_smart_crud.sh
    Tests the generation of a Model with Admin Grid, Form, and Smart UI Inputs.
    """

    def test_smart_crud_generation(self):
        # 1. Setup Module
        module = self.create_module(name='SmartCrud', package='Mage2Gen')
        
        # 2. Add Model with various field types
        snippet = ModelSnippet(module)
        snippet.add(
            name='Article', 
            fields="title:text,content:textarea,publish_date:date,is_active:boolean,category_id:select",
            admin_grid=True,
            admin_form=True
        )

        # 3. Generate
        self.generate(module)

        # 4. Verifications

        # Verify Files Exist
        self.assertFileExists('Model/Article.php')
        self.assertFileExists('view/adminhtml/ui_component/mage2gen_smartcrud_article_form.xml')
        self.assertFileExists('Controller/Adminhtml/Article/MassDelete.php')

        # Verify Form XML Content (The "Smart" parts)
        form_xml_path = 'view/adminhtml/ui_component/mage2gen_smartcrud_article_form.xml'
        
        # Check Date Picker
        self.assertFileContains(form_xml_path, 'formElement="date"')
        
        # Check Toggle (for boolean is_active)
        self.assertFileContains(form_xml_path, '<prefer>toggle</prefer>')
        
        # Check Textarea
        self.assertFileContains(form_xml_path, 'formElement="textarea"')

    def test_mass_actions_generated(self):
        """Ensure mass action controllers are created"""
        module = self.create_module(name='SmartCrud')
        snippet = ModelSnippet(module)
        # is_active:boolean should trigger MassEnable/Disable
        snippet.add(name='Article', fields="is_active:boolean", admin_grid=True)
        self.generate(module)

        self.assertFileExists('Controller/Adminhtml/Article/MassEnable.php')
        self.assertFileExists('Controller/Adminhtml/Article/MassDisable.php')