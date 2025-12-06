from enum import Enum
from .. import Snippet, Phpclass, Phpmethod, Xmlnode, Readme
from ..utils import upperfirst
import os

class Scope(str, Enum):
    ALL = 'all'
    FRONTEND = 'frontend'
    ADMINHTML = 'backend'
    WEBAPI = 'webapi'
    GRAPHQL = 'graphql'

class ObserverSnippet(Snippet):
    snippet_label = 'Observer / Event'
    description = "Create an Observer to hook into Magento events."

    def add(self, event, scope=Scope.ALL):
        split_event = event.split('_')
        observerFolder = ['Observer']
        if scope != Scope.ALL:
            observerFolder.append(scope.value if hasattr(scope, 'value') else scope)
            
        observerFolder.extend([split_event[0], ''.join(upperfirst(item) for item in split_event[1:])])
        observer_class_name = '\\'.join(observerFolder)
        
        observer = Phpclass(
            observer_class_name,
            dependencies=[r'\Magento\Framework\Event\Observer', r'\Magento\Framework\Event\ObserverInterface'],
            implements=['ObserverInterface']
        )
        
        observer.add_method(Phpmethod(
            'execute',
            params=['Observer $observer'],
            body="// Your observer code",
            return_type='void',
            docstring=['Execute observer', '', '@param Observer $observer', '@return void']
        ))

        self.add_class(observer)    

        config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:Event/etc/events.xsd"}, nodes=[
            Xmlnode('event', attributes={'name': event}, nodes=[
                Xmlnode('observer', attributes={
                    'name': '{}_{}'.format(observer.class_namespace.replace('\\', '_').lower(), event),
                    'instance': observer.class_namespace,
                })
            ])
        ])

        xml_path = ['etc']
        if scope == Scope.FRONTEND:
            xml_path.append('frontend')
        elif scope == Scope.ADMINHTML:
            xml_path.append('adminhtml')
        elif scope == Scope.WEBAPI:
            xml_path.append('webapi_rest') 
        elif scope == Scope.GRAPHQL:
            xml_path.append('graphql')

        xml_path.append('events.xml')
        self.add_xml(os.path.join(*xml_path), config)

        self.add_static_file(
            '.',
            Readme(
                specifications=" - Observer\n\t- {} > {}".format(event, observer.class_namespace),
            )
        )