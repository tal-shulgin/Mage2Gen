from tests.integration.base import IntegrationTestBase
from mage2gen.snippets.system import SystemSnippet

class TestSystemConfig(IntegrationTestBase):
    def test_advanced_configuration_options(self):
        """Verify Tooltips, Classes, Restore, and Dependencies"""
        module = self.create_module(name='ConfigSpec')
        snippet = SystemSnippet(module)
        
        # Field 1: Tooltip & CSS
        snippet.add(
            tab='gen', section='spec', group='feat', field='f1',
            tooltip="Helpful tooltip",
            frontend_class="custom-css-class"
        )
        
        # Field 2: canRestore & Config Path
        snippet.add(
            tab='gen', section='spec', group='feat', field='f2',
            can_restore=True,
            config_path="custom/path/val"
        )
        
        # Field 3: Module Dependency
        snippet.add(
            tab='gen', section='spec', group='feat', field='f3',
            if_module_enabled="Magento_Checkout"
        )
        
        self.generate(module)
        
        xml_file = 'etc/adminhtml/system.xml'
        self.assertFileContains(xml_file, '<tooltip>Helpful tooltip</tooltip>')
        self.assertFileContains(xml_file, 'frontend_class="custom-css-class"')
        self.assertFileContains(xml_file, 'canRestore="1"')
        self.assertFileContains(xml_file, 'config_path="custom/path/val"')
        self.assertFileContains(xml_file, '<if_module_enabled>Magento_Checkout</if_module_enabled>')