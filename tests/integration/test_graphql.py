from tests.integration.base import IntegrationTestBase
from mage2gen.snippets.model import ModelSnippet

class TestGraphQL(IntegrationTestBase):
    def test_graphql_crud_generation(self):
        """Verify GraphQL Schema and Resolver generation"""
        module = self.create_module(name='GraphTest')
        snippet = ModelSnippet(module)
        
        snippet.add(
            name="Post",
            fields="title:text,views:int,is_active:boolean",
            graphql=True
        )
        
        self.generate(module)

        # Verify Schema
        self.assertFileContains('etc/schema.graphqls', 'type Query')
        self.assertFileContains('etc/schema.graphqls', 'createPost')
        
        # Verify Resolvers
        self.assertFileExists('Model/Resolver/Post/Get.php')
        self.assertFileExists('Model/Resolver/Post/ListResolver.php')
        self.assertFileExists('Model/Resolver/Post/Save.php')