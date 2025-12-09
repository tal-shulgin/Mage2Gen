from tests.integration.base import IntegrationTestBase
from mage2gen.snippets.extensionattribute import ExtensionAttributeSnippet

class TestExtensionAttributes(IntegrationTestBase):
    def test_extension_attribute_persistence(self):
        """Verify extension attributes with DB persistence logic"""
        module = self.create_module(name='ExtAttrTest')
        snippet = ExtensionAttributeSnippet(module)
        
        snippet.add(
            interface="Magento\\Sales\\Api\\Data\\OrderInterface",
            code="vip_status",
            type="string",
            repository="Magento\\Sales\\Api\\OrderRepositoryInterface",
            table="sales_order"
        )
        
        self.generate(module)

        # XML Checks
        self.assertFileContains('etc/extension_attributes.xml', 'vip_status')
        self.assertFileContains('etc/db_schema.xml', 'sales_order')
        
        # Plugin Logic Check
        plugin_path = 'Plugin/OrderRepositoryPlugin.php'
        self.assertFileContains(plugin_path, 'getVipStatus')
        self.assertFileContains(plugin_path, 'setVipStatus')
        
        # DI Configuration
        self.assertFileContains('etc/di.xml', 'OrderRepositoryPlugin')