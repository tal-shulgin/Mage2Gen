import unittest
import os
import shutil
import tempfile
from xml.etree import ElementTree as ET

# We rely on PYTHONPATH being set correctly (via Docker/Makefile)
from mage2gen import Module

class IntegrationTestBase(unittest.TestCase):
    """
    Base class for Integration Tests.
    Generates modules into a temporary sandbox for validation.
    """

    def setUp(self):
        # Create a unique temp directory for every test execution
        self.test_dir = tempfile.mkdtemp()
        self.package_name = 'TestVendor'
        self.module_name = 'TestModule'
        self.module_path = os.path.join(self.test_dir, self.package_name, self.module_name)

    def tearDown(self):
        # Cleanup: Remove the temp directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_module(self, name='TestModule', package='TestVendor', description='Integration Test'):
        """Helper to initialize a module object"""
        self.package_name = package
        self.module_name = name
        self.module_path = os.path.join(self.test_dir, package, name)
        return Module(package, name, description)

    def generate(self, module_obj):
        """Triggers the generation process"""
        module_obj.generate_module(self.test_dir)

    # --- Assertion Helpers ---

    def assertFileExists(self, relative_path):
        """Check if a file exists relative to the generated module root"""
        full_path = os.path.join(self.module_path, relative_path)
        self.assertTrue(os.path.exists(full_path), f"File missing: {relative_path}")

    def assertFileContains(self, relative_path, string_content):
        """Check if file contains specific string"""
        full_path = os.path.join(self.module_path, relative_path)
        self.assertFileExists(relative_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(string_content, content, f"String '{string_content}' not found in {relative_path}")

    def get_xml_root(self, relative_path):
        """Parses an XML file and returns the root element"""
        full_path = os.path.join(self.module_path, relative_path)
        self.assertFileExists(relative_path)
        try:
            tree = ET.parse(full_path)
            return tree.getroot()
        except ET.ParseError as e:
            self.fail(f"Invalid XML in {relative_path}: {e}")

    def assertXmlHasNode(self, relative_path, xpath, namespaces=None):
        """
        Asserts that an XML file contains a node matching the XPath.
        Note: ElementTree XPath support is limited.
        """
        root = self.get_xml_root(relative_path)
        
        # Simple non-namespace search if no namespaces provided
        # For complex XML (like layout), you might need to strip namespaces or provide map
        if namespaces:
            nodes = root.findall(xpath, namespaces)
        else:
            # Fallback: simple search or iteration for checking existence
            nodes = root.findall(xpath)
            
        self.assertTrue(len(nodes) > 0, f"XPath '{xpath}' not found in {relative_path}")
        return nodes