from tests.integration.base import IntegrationTestBase
from mage2gen.snippets.model import ModelSnippet
from mage2gen.snippets.viewmodel import ViewModelSnippet
from mage2gen.snippets.integrationtest import IntegrationTestSnippet

class TestFrontendBackend(IntegrationTestBase):
    def test_admin_menu_parent(self):
        """Verify menu nesting logic"""
        module = self.create_module(name='MenuTest')
        snippet = ModelSnippet(module)
        
        snippet.add(
            name="Banner",
            fields="title:text",
            admin_grid=True,
            menu_parent="Magento_Backend::content"
        )
        
        self.generate(module)
        
        # Should NOT have top level menu
        menu_path = 'etc/adminhtml/menu.xml'
        self.assertFileContains(menu_path, 'parent="Magento_Backend::content"')

    def test_view_model_injection(self):
        """Verify ViewModel creation and layout injection"""
        module = self.create_module(name='VMTest')
        snippet = ViewModelSnippet(module)
        
        snippet.add(
            classname="BannerLogic",
            methodname="getData",
            layout_handle="default",
            reference_name="header.container"
        )
        
        self.generate(module)
        
        self.assertFileExists('ViewModel/BannerLogic.php')
        self.assertFileContains('view/frontend/layout/default.xml', 'argument name="view_model"')

    def test_generated_integration_test(self):
        """Verify generation of Magento Integration Tests"""
        module = self.create_module(name='QualityTest')
        snippet = IntegrationTestSnippet(module)
        
        snippet.add(
            repository="Vendor\\Mod\\Api\\RepoInterface",
            data_interface="Vendor\\Mod\\Api\\DataInterface",
            test_field="title"
        )
        
        self.generate(module)
        
        test_file = 'Test/Integration/Model/RepoInterfaceTest.php'
        self.assertFileExists(test_file)
        self.assertFileContains(test_file, 'testCrudOperations')