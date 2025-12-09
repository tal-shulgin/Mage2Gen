from tests.integration.base import IntegrationTestBase
from mage2gen.snippets.messagequeue import MessageQueueSnippet

class TestAsync(IntegrationTestBase):
    def test_message_queue_topology(self):
        """Verify RabbitMQ/Mysql queue generation"""
        module = self.create_module(name='AsyncTest')
        snippet = MessageQueueSnippet(module)
        
        snippet.add(
            topic="mage2gen.async.test",
            consumer="LogConsumer",
            queue="mage2gen_async_log",
            exchange="magento",
            schema_type="string"
        )
        
        self.generate(module)

        # Verify XML Configuration
        self.assertFileExists('etc/communication.xml')
        self.assertFileExists('etc/queue_topology.xml')
        self.assertFileExists('etc/queue_consumer.xml')
        
        # Verify Consumer logic
        self.assertFileContains('Model/Consumer/LogConsumer.php', 'processMessage')
        
        # Verify Publisher generation
        self.assertFileContains('Model/Publisher/Mage2genAsyncTestPublisher.php', 'mage2gen.async.test')