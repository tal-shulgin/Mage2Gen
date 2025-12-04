# A Magento 2 module generator library
# Copyright (C) 2025 Mage2Gen
import os
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme
from ..utils import upperfirst

class MessageQueueSnippet(Snippet):
    snippet_label = 'Message Queue'
    description = """
    Create a Message Queue configuration with a Topic, Exchange, Queue, and Consumer.
    Optionally generates a Publisher class wrapper for easy message dispatching.
    """

    def add(self, topic, consumer, queue, exchange, handler_method='processMessage', schema_type='string', generate_publisher=False, extra_params=None):
        
        # 1. Create Consumer Class
        consumer_class_name = 'Model\\Consumer\\{}'.format(upperfirst(consumer))
        consumer_class = Phpclass(
            consumer_class_name,
            dependencies=['Psr\\Log\\LoggerInterface']
        )
        
        consumer_class.add_method(Phpmethod(
            '__construct',
            params=['LoggerInterface $logger'],
            body='$this->logger = $logger;',
            docstring=['@param LoggerInterface $logger'],
            access='public'
        ))
        
        consumer_class.attributes = ['/** @var LoggerInterface */', 'private $logger;']

        # Determine param type based on schema
        param_type = 'string'
        if schema_type != 'string':
            # Assume it's a class interface if not string
            param_type = '\\' + schema_type.lstrip('\\')

        consumer_class.add_method(Phpmethod(
            handler_method,
            params=['{} $message'.format(param_type)],
            return_type='void',
            body="""$this->logger->info('Processing message', ['message' => $message]);
// Add your message processing logic here""",
            docstring=[
                'Process message',
                '',
                '@param {} $message'.format(param_type),
                '@return void'
            ]
        ))
        
        self.add_class(consumer_class)

        # --- NEW: Publisher Generation ---
        publisher_info = ""
        if generate_publisher:
            # Derive class name from topic: "my.topic.name" -> "MyTopicName"
            topic_parts = topic.split('.')
            topic_class_name = ''.join(part.capitalize() for part in topic_parts)
            publisher_class_name = 'Model\\Publisher\\{}'.format(topic_class_name)

            publisher_class = Phpclass(
                publisher_class_name,
                dependencies=['Magento\\Framework\\MessageQueue\\PublisherInterface']
            )

            publisher_class.attributes = [
                "const TOPIC_NAME = '{}';".format(topic),
                '/** @var PublisherInterface */',
                'private $publisher;'
            ]

            publisher_class.add_method(Phpmethod(
                '__construct',
                params=['PublisherInterface $publisher'],
                body='$this->publisher = $publisher;',
                docstring=['@param PublisherInterface $publisher'],
                access='public'
            ))

            publisher_class.add_method(Phpmethod(
                'publish',
                # Use the same type hint as the consumer for type safety
                params=['{} $data'.format(param_type)], 
                return_type='void',
                body="$this->publisher->publish(self::TOPIC_NAME, $data);",
                docstring=[
                    'Publish message to topic',
                    '',
                    '@param {} $data'.format(param_type),
                    '@return void'
                ]
            ))

            self.add_class(publisher_class)
            publisher_info = "\n\t- Publisher: {}".format(publisher_class_name)

        # 2. communication.xml
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

        # 3. queue_consumer.xml
        cons_xml = Xmlnode('config', attributes={
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework-message-queue:etc/consumer.xsd"
        }, nodes=[
            Xmlnode('consumer', attributes={
                'name': consumer,
                'queue': queue,
                'connection': 'amqp',
                'consumerInstance': r'Magento\Framework\MessageQueue\Consumer',
                'handler': '{}::{}'.format(consumer_class.class_namespace, handler_method)
            })
        ])
        self.add_xml('etc/queue_consumer.xml', cons_xml)

        # 4. queue_topology.xml
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
                    'id': '{}_{}'.format(exchange, queue),
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
                specifications=" - Message Queue\n\t- Topic: {}\n\t- Consumer: {}{}".format(topic, consumer, publisher_info),
            )
        )

    @classmethod
    def params(cls):
        return [
            SnippetParam('topic', required=True, description='e.g. my.module.topic'),
            SnippetParam('consumer', required=True, description='Unique name for the consumer', regex_validator=r'^[a-zA-Z0-9_]+$'),
            SnippetParam('queue', required=True, description='Queue name', regex_validator=r'^[a-zA-Z0-9_]+$'),
            SnippetParam('exchange', required=True, description='Exchange name', regex_validator=r'^[a-zA-Z0-9_]+$'),
            SnippetParam('handler_method', required=True, default='processMessage', description='Method name in consumer class'),
            SnippetParam('schema_type', required=True, default='string', description='Data interface class or simple type (string, bool, etc)'),
            SnippetParam('generate_publisher', required=False, default=False, yes_no=True, description='Generate a Publisher class wrapper?')
        ]