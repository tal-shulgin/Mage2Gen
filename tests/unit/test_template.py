import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from mage2gen.core.template import TemplateEngine

class TestTemplate(unittest.TestCase):
    
    def test_env_initialization(self):
        env = TemplateEngine.get_env()
        self.assertIsNotNone(env)
        
    def test_render_string(self):
        # Verify Jinja2 behavior
        env = TemplateEngine.get_env()
        t = env.from_string("Hello {{ name }}")
        self.assertEqual(t.render(name="Mage2Gen"), "Hello Mage2Gen")

    def test_render_file(self):
        # Test loading a real template (e.g. registration.j2)
        result = TemplateEngine.render('registration.j2', {
            'license': '',
            'module_name': 'Vendor_Module'
        })
        self.assertIn("ComponentRegistrar::register", result)
        self.assertIn("'Vendor_Module'", result)

if __name__ == '__main__':
    unittest.main()