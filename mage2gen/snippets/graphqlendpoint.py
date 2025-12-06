from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst, lowerfirst

class GraphQlEndpointSnippet(Snippet):
    snippet_label = 'GraphQl Endpoint'
    description = "Create a GraphQl Query or Mutation."

    def add(self, base_type='Query', identifier=None, **kwargs):
        # Support legacy argument names
        if identifier is None and 'custom_type' in kwargs:
            identifier = kwargs['custom_type']
            base_type = 'Custom' # Infer custom
            
        if not identifier:
            raise ValueError("Identifier required")

        package = self._module.package
        module = self._module.name
        
        field_name = lowerfirst(identifier)
        class_name = upperfirst(field_name)
        
        resolver_class = f"{package}\\{module}\\Model\\Resolver\\{class_name}"
        
        # 1. Resolver Class
        resolver_content = TemplateEngine.render('snippets/graphql/resolver.j2', {
            'namespace': f"{package}\\{module}\\Model\\Resolver",
            'class_name': class_name
        })
        self.add_static_file(f"Model/Resolver/{class_name}", StaticFile(f"{class_name}.php", body=resolver_content))
        
        # 2. Schema GraphQL
        # Simplified generation for V3: We append string to schema.graphqls file via StaticFile
        # instead of building object graph.
        
        output_type_name = f"{class_name}Output"
        args_str = "" # TODO: Add arguments support if needed
        
        schema_content = TemplateEngine.render('snippets/graphql/schema.j2', {
            'type_name': base_type,
            'field_name': field_name,
            'args': args_str,
            'return_type': output_type_name,
            'resolver_class': resolver_class.replace('\\', '\\\\'), # GraphQL requires double slash
            'description': f"{base_type} field {field_name}",
            'output_type': True
        })
        
        self.add_static_file('etc/schema.graphqls', StaticFile('schema.graphqls', body=schema_content))
        
        # 3. Module Sequence
        config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
            Xmlnode('module', attributes={'name': f"{package}_{module}"}, nodes=[
                Xmlnode('sequence', attributes={}, nodes=[
                    Xmlnode('module', attributes={'name': 'Magento_GraphQl'})
                ])
            ])
        ])
        self.add_xml('etc/module.xml', config)

        self.add_static_file('.', Readme(specifications=f" - GraphQL: {base_type} {field_name}"))