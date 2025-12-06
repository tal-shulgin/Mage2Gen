import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from mage2gen.core.template import TemplateEngine

class TestTemplate(unittest.TestCase):
    
    def test_render(self):
        # We need a dummy template, or we can use string loading for testing if needed,
        # but PackageLoader requires a file.
        # For this test, I assume 'test.j2' exists or I mock it.
        # Let's rely on checking if the Env loads correctly.
        
        env = TemplateEngine.get_env()
        self.assertIsNotNone(env)
        
        # Test basic jinja functionality manually
        t = env.from_string("Hello {{ name }}")
        result = t.render(name="World")
        self.assertEqual(result, "Hello World")

if __name__ == '__main__':
    unittest.main()