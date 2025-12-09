import unittest
from mage2gen import Module
from mage2gen.snippets import GraphQlEndpointSnippet
from tests import utils

class TestSnippetGraphQLV3(unittest.TestCase):

    def test_query_generation(self):
        module = Module(package='Test', name='Module', description='Desc')
        snippet = GraphQlEndpointSnippet(module)
        
        # Add Query
        snippet.add(
            base_type='Query',
            identifier='getRecentPosts'
        )

        result = utils.CodeSniffer.generate_and_test(module)
        self.assertTrue(result)
        
        # Verify Resolver
        files = list(module._static_files.keys())
        self.assertTrue(any('GetRecentPosts.php' in f for f in files))
        
        # Verify Schema
        # In V3 we use StaticFile for schema.graphqls
        self.assertTrue(any('schema.graphqls' in f for f in files))

    def tearDown(self):
        utils.CodeSniffer.cleanup()