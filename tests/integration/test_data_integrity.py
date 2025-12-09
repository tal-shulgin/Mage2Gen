from tests.integration.base import IntegrationTestBase
from mage2gen.snippets.model import ModelSnippet

class TestDataIntegrity(IntegrationTestBase):
    def test_complex_data_handling(self):
        """Verify JSON serialization and Image handling in Resource Models"""
        module = self.create_module(name='DataCheck')
        snippet = ModelSnippet(module)
        
        # Multiselect triggers JSON serialization, Image triggers array handling
        snippet.add(
            name="Portfolio",
            fields="title:text,categories:multiselect,thumbnail:image",
            admin_grid=True
        )
        
        self.generate(module)
        
        res_file = 'Model/ResourceModel/Portfolio.php'
        
        # Check Serialization Logic
        self.assertFileContains(res_file, '_beforeSave')
        self.assertFileContains(res_file, 'json->serialize')
        self.assertFileContains(res_file, '_afterLoad')
        self.assertFileContains(res_file, 'json->unserialize')
        
        # Check Image Array Logic
        self.assertFileContains(res_file, "isset($image[0]['name'])")