import unittest
import os
from mage2gen import Module
from mage2gen.features.admin_crud import AdminCrudFeature
from tests import utils

class TestFeatureAdminCrud(unittest.TestCase):

    def test_feature_generation(self):
        """Test that AdminCrud feature generates Models AND Controllers"""
        module = Module(package='Mage2Gen', name='Blog', description='Blog Module')
        feature = AdminCrudFeature(module)
        
        # Generate a Post entity with title and content
        feature.add(name='Post', fields='title:text,content:textarea')

        # We are checking if the generation runs without error
        result = utils.CodeSniffer.generate_and_test(module)
        self.assertTrue(result)
        
        # Check generated files in internal state
        # Because V3 uses StaticFile internally, we check module._static_files
        
        static_files = module._static_files.keys()
        
        # Check for Model
        # The key is full path, e.g. "Model/Post.php"
        # We need to be careful about path separators in test env
        
        has_model = any('Model/Post.php' in f for f in static_files)
        self.assertTrue(has_model, f"Model/Post.php not found. Files: {list(static_files)}")
        
        # Check for Controllers
        has_controller_index = any('Controller/Adminhtml/Post/Index.php' in f for f in static_files)
        self.assertTrue(has_controller_index, "Index Controller not found")
        
        has_controller_save = any('Controller/Adminhtml/Post/Save.php' in f for f in static_files)
        self.assertTrue(has_controller_save, "Save Controller not found")

    def tearDown(self):
        utils.CodeSniffer.cleanup()