import os
from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class MessageQueueSnippet(Snippet):
    snippet_label = 'Message Queue'
    description = """
    Create a Message Queue configuration (RabbitMQ/Mysql) with Topic, Exchange, Queue, Consumer, and Publisher.
    """

    def add(self, topic, consumer, queue, exchange, handler_method='processMessage', schema_type='string', generate_publisher=True, extra_params=None):
        package = self._module.package
        module = self._module.name
        
        # 1. Consumer Class
        consumer_class_name = upperfirst(consumer)
        consumer_ns = f"{package}\\{module}\\Model\\Consumer"
        
        # Determine PHP type hint
        type_hint = 'string'
        if schema_type != 'string':
            # FIX: Logic moved outside f-string to avoid SyntaxError
            clean_schema = schema_type.lstrip('\\')
            type_hint = f"\\{clean_schema}"

        consumer_content = TemplateEngine.render('snippets/messagequeue/consumer.j2', {
            'namespace': consumer_ns,
            'class_name': consumer_class_name,
            'method_name': handler_method,
            'type_hint': type_hint
        })
        self.add_static_file(f"Model/Consumer", StaticFile(f"{consumer_class_name}.php", body=consumer_content))

        # 2. Publisher Class (Optional)
        publisher_info = ""
        if generate_publisher:
            # Derive class name from topic: "my.topic.name" -> "MyTopicName"
            topic_parts = topic.split('.')
            topic_class_name = ''.join(part.capitalize() for part in topic_parts)
            publisher_class_name = f"{topic_class_name}Publisher"
            publisher_ns = f"{package}\\{module}\\Model\\Publisher"

            publisher_content = TemplateEngine.render('snippets/messagequeue/publisher.j2', {
                'namespace': publisher_ns,
                'class_name': publisher_class_name,
                'topic': topic
            })
            self.add_static_file(f"Model/Publisher", StaticFile(f"{publisher_class_name}.php", body=publisher_content))
            publisher_info = f"\n\t- Publisher: {publisher_class_name}"

        # 3. XML Configuration
        
        # communication.xml
        comm_xml = Xmlnode('config', attributes={
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Communication/etc/communication.xsd"
        }, nodes=[
            Xmlnode('topic', attributes={
                'name': topic,
                'request': schema_type
            })
        ])
        self.add_xml('etc/communication.xml', comm_xml)

        # queue_consumer.xml
        consumer_full_class = f"{consumer_ns}\\{consumer_class_name}"
        cons_xml = Xmlnode('config', attributes={
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework-message-queue:etc/consumer.xsd"
        }, nodes=[
            Xmlnode('consumer', attributes={
                'name': f"{package.lower()}.{module.lower()}.{consumer.lower()}",
                'queue': queue,
                'connection': 'amqp', # Default to RabbitMQ
                'consumerInstance': r'Magento\Framework\MessageQueue\Consumer',
                'handler': f"{consumer_full_class}::{handler_method}"
            })
        ])
        self.add_xml('etc/queue_consumer.xml', cons_xml)

        # queue_topology.xml
        top_xml = Xmlnode('config', attributes={
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework-message-queue:etc/topology.xsd"
        }, nodes=[
            Xmlnode('exchange', attributes={
                'name': exchange,
                'type': 'topic',
                'connection': 'amqp'
            }, nodes=[
                Xmlnode('binding', attributes={
                    'id': f"{exchange}_{queue}",
                    'topic': topic,
                    'destinationType': 'queue',
                    'destination': queue
                })
            ])
        ])
        self.add_xml('etc/queue_topology.xml', top_xml)

        self.add_static_file(
            '.',
            Readme(
                specifications=f" - Message Queue\n\t- Topic: {topic}\n\t- Queue: {queue}{publisher_info}",
            )
        )

    @classmethod
    def params(cls):
        return [
            SnippetParam('topic', required=True, description='e.g. mage2gen.module.topic'),
            SnippetParam('consumer', required=True, description='Consumer Class Name (e.g. ExportConsumer)', regex_validator=r'^[a-zA-Z0-9_]+$'),
            SnippetParam('queue', required=True, description='Queue name (e.g. mage2gen_export)', regex_validator=r'^[a-zA-Z0-9_]+$'),
            SnippetParam('exchange', required=True, description='Exchange name (e.g. magento)', regex_validator=r'^[a-zA-Z0-9_]+$'),
            SnippetParam('handler_method', required=False, default='processMessage', description='Method name in consumer class'),
            SnippetParam('schema_type', required=False, default='string', description='Data interface or simple type'),
            SnippetParam('generate_publisher', required=False, default=True, yes_no=True, description='Generate a Publisher class wrapper?')
        ]