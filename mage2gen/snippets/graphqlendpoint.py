# A Magento 2 module generator library
# Copyright (C) 2018 Lewis Voncken
#
# This file is part of Mage2Gen.
import os
from .. import Module, Phpclass, Phpmethod, Xmlnode, Snippet, SnippetParam, GraphQlSchema, GraphQlObjectType, \
    GraphQlObjectItem, StaticFile, Readme
from ..utils import upperfirst, lowerfirst


class GraphQlEndpointSnippet(Snippet):
    snippet_label = 'GraphQl Endpoint'

    description = """
    Create a GraphQl Endpoint (Query or Mutation).
    """

    GRAPHQL_TYPE_CHOISES = [
        ('Query', 'Query'),
        ('Mutation', 'Mutation'),
        ('Custom', 'Custom')
    ]

    def add(self, base_type, identifier, custom_type=False, description='', object_arguments=False, object_fields=False,
            data_provider_dependency=False, add_cache_identity=False, extra_params=None):

        if not object_fields:
            object_fields = 'id'
            if object_arguments:
                object_fields = object_arguments

        if custom_type:
            identifier = custom_type
        
        identifier = lowerfirst(identifier)
        item_identifier = upperfirst(identifier)
        
        resolver_classname = 'Model\\Resolver\\{}'.format(item_identifier)
        resolver_graphqlformat = '{}\\\{}\\\{}'.format(self._module.package, self._module.name, resolver_classname)

        cache_identity_graphqlformat = ''
        if add_cache_identity and item_identifier and base_type == 'Query':
            object_id = object_fields.split(',')[0]
            cache_identity_graphqlformat = '{}\\\{}\\\Model\\\Resolver\\\{}\\\\Identity'.format(self._module.package, self._module.name, item_identifier)
            
            # Create Identity Class
            cacheIdentity = Phpclass(
                'Model\\Resolver\\{}\\Identity'.format(item_identifier),
                implements=['IdentityInterface'],
                dependencies=['Magento\\Framework\\GraphQl\\Query\\Resolver\\IdentityInterface'],
                attributes=['private $cacheTag = \Magento\Framework\App\Config::CACHE_TAG;']
            )
            cacheIdentity.add_method(Phpmethod(
                'getIdentities',
                params=['array $resolvedData'],
                body="""$ids = empty($resolvedData['{object_id}']) ? [] : [$this->cacheTag, sprintf('%s_%s', $this->cacheTag, $resolvedData['{object_id}'])];
return $ids;""".format(object_id=object_id),
                docstring=['@inheritdoc']
            ))
            self.add_class(cacheIdentity)

        # Define Output Type
        return_type_name = 'String'
        
        if base_type == 'Custom':
            return_type_name = identifier
        elif base_type == 'Query':
            return_type_name = item_identifier + 'Output'
        elif base_type == 'Mutation':
            return_type_name = item_identifier + 'Output'

        # Define Input Type Name (for Mutations)
        input_type_name = item_identifier + 'Input'

        schema = GraphQlSchema()

        # 1. Add the Operation to schema (Query/Mutation)
        if base_type != 'Custom':
            base_object_type = GraphQlObjectType(base_type)
            
            # Argument string construction
            # Query: field(id: Int): Output
            # Mutation: field(input: Input!): Output
            
            item_args_str = object_arguments
            item_input_def = False

            if base_type == 'Mutation':
                # Enforce strict input object for mutations
                item_args_str = 'input: {}!'.format(input_type_name)
                item_input_def = input_type_name + '!'

            base_object_type.add_objectitem(
                GraphQlObjectItem(
                    identifier,
                    item_arguments=item_args_str,
                    item_input=item_input_def,
                    item_type=return_type_name,
                    item_resolver=resolver_graphqlformat,
                    item_cache_identity=cache_identity_graphqlformat,
                    description=description,
                    base_type=base_type
                )
            )
            schema.add_objecttype(base_object_type)

        # 2. Define the Output Object Type
        # type IdentifierOutput { ... }
        if base_type in ['Query', 'Mutation']:
            output_definition = GraphQlObjectType(return_type_name)
            for field in object_fields.split(','):
                output_definition.add_objectitem(
                    GraphQlObjectItem(field.strip(), description="Output field " + field.strip())
                )
            schema.add_objecttype(output_definition)

        # 3. Define the Input Object Type (Mutation only)
        # input IdentifierInput { ... }
        if base_type == 'Mutation':
            input_definition = GraphQlObjectType(input_type_name, type_declaration='input')
            for arg in object_arguments.split(','):
                input_definition.add_objectitem(
                    GraphQlObjectItem(arg.strip(), description="Input field " + arg.strip())
                )
            schema.add_objecttype(input_definition)

        self.add_graphqlschema('etc/schema.graphqls', schema)

        # --- Create PHP Resolver ---
        
        resolver_deps = [
            'Magento\\Framework\\GraphQl\\Config\\Element\\Field',
            'Magento\\Framework\\GraphQl\\Query\\ResolverInterface',
            'Magento\\Framework\\GraphQl\\Schema\\Type\\ResolveInfo',
        ]
        resolver = Phpclass(
            resolver_classname,
            implements=['ResolverInterface'],
            dependencies=resolver_deps
        )

        resolve_body = "return ['status' => 'success'];"
        if base_type == 'Query':
            resolve_body = "return []; // Return data matching " + return_type_name

        resolver.add_method(Phpmethod(
            'resolve',
            params=[
                'Field $field',
                '$context',
                'ResolveInfo $info',
                'array $value = null',
                'array $args = null'
            ],
            body=resolve_body,
            docstring=['@inheritdoc']
        ))

        self.add_class(resolver)

        # Module sequence
        etc_module = Xmlnode('config', attributes={
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
            Xmlnode('module', attributes={'name': self.module_name}, nodes=[
                Xmlnode('sequence', attributes={}, nodes=[
                    Xmlnode('module', attributes={'name': 'Magento_GraphQl'})
                ])
            ])
        ])
        self.add_xml('etc/module.xml', etc_module)

        self.add_static_file(
            '.',
            Readme(
                specifications=" - GraphQl Endpoint\n\t- {} ({})".format(identifier, base_type),
            )
        )

    @classmethod
    def params(cls):
        return [
            SnippetParam(name='base_type', choises=cls.GRAPHQL_TYPE_CHOISES, default='Query'),
            SnippetParam(
                name='custom_type', required=True,
                depend={'base_type': 'Custom'},
                description='Example: products',
                regex_validator=r'^[a-zA-Z\d\-_\s]+$',
                error_message='Only alphanumeric'
            ),
            SnippetParam(
                name='identifier', required=True,
                depend={'base_type': r'Query|Mutation'},
                description='Example: createProduct',
                regex_validator=r'^[a-zA-Z\d\-_\s]+$',
                error_message='Only alphanumeric'
            ),
            SnippetParam(
                name='description',
                description='Short description',
                required=False
            ),
            SnippetParam(
                name='object_arguments',
                depend={'base_type': r'Query|Mutation'},
                required=False,
                description='comma seperated args (e.g. id,name)',
                error_message='Only alphanumeric'
            ),
            SnippetParam(
                name='object_fields',
                required=False,
                depend={'base_type': r'Query|Custom'},
                description='comma seperated fields (e.g. sku,price)',
                error_message='Only alphanumeric'
            ),
            SnippetParam(
                name='data_provider_dependency',
                required=False,
                depend={'base_type': 'Query'},
                description='Example: Magento\Store\Api\StoreConfigManagerInterface',
                regex_validator=r'^[\w\\]+$',
                error_message='Only alphanumeric, underscore and backslash characters are allowed'
            ),
             SnippetParam(
                name='add_cache_identity',
                required=True,
                depend={'base_type': 'Query'},
                default=False,
                yes_no=True),
        ]
