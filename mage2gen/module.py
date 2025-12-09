# A Magento 2 module generator library
# Copyright (C) 2025 Mage2Gen
import os
import json
import textwrap
from collections import defaultdict, OrderedDict
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom

# Import the new prettify function
from .utils import upperfirst, merge_xml_files, prettify_xml
from .core.template import TemplateEngine

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

###############################################################################
# PHP Class
###############################################################################
class Phpclass:
    template_file = os.path.join(TEMPLATE_DIR, 'class.j2')

    def __init__(self, class_namespace, extends=None, implements=None, attributes=None, dependencies=None, abstract=False):
        self.class_namespace = self.upper_class_namespace(class_namespace)
        self.methods = []
        self.extends = extends
        self.implements = implements if implements else []
        self.attributes = attributes if attributes else []
        self.dependencies = dependencies if dependencies else []
        self.abstract = abstract
        self.license = None

    def __eq__(self, other):
        return self.class_namespace == other.class_namespace

    def __add__(self, other):
        self.attributes = set(list(self.attributes) + list(other.attributes))
        self.implements = set(list(self.implements) + list(other.implements))
        self.dependencies = set(list(self.dependencies) + list(other.dependencies))
        for method in other.methods:
            self.add_method(method)
        return self

    @property
    def class_name(self):
        return self.class_namespace.split('\\')[-1]

    @property
    def namespace(self):
        return '\\'.join(self.class_namespace.split('\\')[:-1])

    def upper_class_namespace(self, class_namespace):
        return '\\'.join(upperfirst(n) for n in class_namespace.strip('\\').split('\\'))

    def add_method(self, method):
        if method in self.methods:
            method_index = self.methods.index(method)
            self.methods[method_index] = self.methods[method_index] + method
        else:
            self.methods.append(method)

    def context_data(self):
        # dependencies
        dependencies_str = ''
        if self.dependencies:
            # Add two newlines before use statements to separate from namespace
            dependencies_str = '\n\n' + ';\n'.join("use %s" % (d) for d in sorted(self.dependencies)) + ';'

        # Build Class Body
        body_parts = []

        # 1. Attributes
        valid_attrs = [a for a in self.attributes if a.strip()]
        if valid_attrs:
            sorted_attrs = sorted(list(valid_attrs), key=lambda x: (not x.startswith('const'), x))
            # Add indentation
            body_parts.append('    ' + '\n    '.join(sorted_attrs))

        # 2. Methods
        if self.methods:
            body_parts.append('\n\n'.join(m.generate() for m in self.methods))

        # Join attributes and methods with a blank line
        class_body = '\n\n'.join(body_parts)

        return {
            'license': self.license.get_php_docstring() if self.license else '',
            'namespace': self.namespace,
            'class_name': self.class_name,
            'class_body': class_body,
            'extends': ' extends {}'.format(self.extends) if self.extends else '',
            'implements': ' implements {}'.format(', '.join(self.implements)) if self.implements else '',
            'dependencies': dependencies_str,
            'abstract': 'abstract ' if self.abstract else '',
        }

    def generate(self):
        return TemplateEngine.render('class.j2', self.context_data())

    def save(self, root_location):
        path = os.path.join(root_location, self.class_namespace.replace('\\', '/') + '.php')
        try:
            os.makedirs(os.path.dirname(path))
        except Exception:
            pass

        with open(path, 'w+', encoding='utf-8') as class_file:
            class_file.writelines(self.generate())

class Phpmethod:
    PUBLIC = 'public'
    PROTECTED = 'protected'
    PRIVATE = 'private'

    def __init__(self, name, **kwargs):
        self.name = name
        self.access = kwargs.get('access', self.PUBLIC)
        self.params = kwargs.get('params', [])
        self.return_type = kwargs.get('return_type', '')
        self.docstring = kwargs.get('docstring', [])
        self.body = [kwargs.get('body', '')]
        self.end_body = [kwargs.get('end_body', '')]
        self.body_start = kwargs.get('body_start', '')
        self.body_return = kwargs.get('body_return', '')
        self.template_file = os.path.join(TEMPLATE_DIR, 'method.tmpl')

    def __eq__(self, other):
        return self.name == other.name

    def __add__(self, other):
        for code in other.body:
            if code not in self.body:
                self.body.append(code)
        for code in other.end_body:
            if code not in self.end_body:
                self.end_body.insert(0, code)

        for param in other.params:
            if param not in self.params:
                self.params.append(param)
        return self

    def __hash__(self):
        return hash(self.name)

    def params_code(self):
        raw_length = sum(len(s) for s in self.params)
        # PSR-12: if multiline, newline after ( and before )
        if raw_length > 80 or len(self.params) > 3:
            return '\n        ' + ',\n        '.join(self.params) + '\n    '
        else:
            return ', '.join(self.params)

    def return_type_code(self):
        if self.return_type:
            return ': ' + self.return_type
        return ''

    def docstring_code(self):
        if not self.docstring:
            return ''
        # Indent 4 spaces
        docstring = '    /**'
        docstring += '\n     *' + '\n     *'.join(" {}".format(line.strip()) if len(line.strip()) else '' for line in self.docstring)
        docstring += '\n     */'
        return docstring

    def add_body_code(self, code):
        if code not in self.body:
            self.append(code)

    def body_code(self):
        full_body_list = []
        if self.body_start:
            full_body_list.append(self.body_start)
        full_body_list.extend(self.body)
        full_body_list.extend(self.end_body)
        if self.body_return:
            full_body_list.append(self.body_return)

        processed_body = []
        for block in full_body_list:
            if not block.strip():
                continue
            # Normalize indentation
            dedented = textwrap.dedent(block)
            # Indent 8 spaces for method body
            indented = textwrap.indent(dedented.strip(), '        ')
            processed_body.append(indented)
        
        return '\n\n'.join(processed_body)

    def generate(self):
        return TemplateEngine.render('method.j2', {
            'method': self.name,
            'access': self.access,
            'docstring': self.docstring_code(),
            'params': self.params_code(),
            'return_type': self.return_type_code(),
            'body': self.body_code()
        }).replace('\t', '    ')

###############################################################################
# XML
###############################################################################
class Xmlnode:
    def __init__(self, node_name, attributes=None, nodes=None, node_text=None, match_attributes=None, xsd=False):
        if nodes :
            nodes = [x for x in nodes if x]
        self.node_name = node_name
        self.node_text = node_text
        self.attributes = attributes if attributes else {}
        self.match_attributes = match_attributes if match_attributes else ['name', 'id', 'for', 'referenceId']
        self.nodes = nodes if nodes else []
        self.xsd = xsd

    def __str__(self):
        return self.node_name

    def __eq__(self, other):
        if self.node_name != other.node_name:
            return False
        for key in self.match_attributes:
            if key in self.attributes and self.attributes[key] != other.attributes[key]:
                    return False
        return True

    def output_tree(self, depth=0):
        output = ("  " * depth) + "<{} {}>\n".format(self.node_name, self.attributes)
        for node in self.nodes:
            output += node.output_tree(depth + 1)
        return output

    def add_nodes(self, nodes):
        for node in nodes:
            if node in self.nodes and node.nodes:
                index = self.nodes.index(node)
                self.nodes[index].add_nodes(node.nodes)
            elif node not in self.nodes:
                self.nodes.append(node)

    def generate(self, element=None):
        if element != None:
            el = SubElement(element, self.node_name)
        else:
            el = Element(self.node_name)
            if not self.xsd:
                el.set('xmlns:xsi',"http://www.w3.org/2001/XMLSchema-instance")

        if self.node_text:
            el.text = self.node_text

        # Attributes are set here. 
        for key, value in self.attributes.items():
            el.set(str(key), str(value))

        for node in self.nodes:
            node.generate(el)

        if element == None:
            return prettify_xml(el)

    def save(self, xml_path):
        try:
            os.makedirs(os.path.dirname(xml_path))
        except Exception:
            pass
        
        new_content = self.generate()
        
        if os.path.exists(xml_path):
            final_content = merge_xml_files(xml_path, new_content)
        else:
            final_content = new_content

        with open(xml_path, 'w+', encoding='utf-8') as xml_file:
            xml_file.write(final_content)

###############################################################################
# StaticFile
###############################################################################
class StaticFile:
    def __init__(self, file_name, body=None, template_file=None, context_data=None):
        self.file_name = file_name
        self.template_file = template_file
        self._context_data = context_data if context_data else {}
        self._context_data['body'] = [body] if body else []

    def __add__(self, other):
        for code in other._context_data['body']:
            if code not in self._context_data['body']:
                self._context_data['body'].append(code)
        return self

    def context_data(self):
        data = self._context_data
        data['body'] = "\n\n".join(self._context_data['body'])
        return self._context_data

    def generate(self):
        if self.template_file:
            if self.template_file.endswith('.j2'):
                return TemplateEngine.render(self.template_file, self.context_data())
            
            # V2 Legacy
            with open(os.path.join(TEMPLATE_DIR, self.template_file), 'rb') as tmpl:
                template = tmpl.read().decode('utf-8')
            return template.format(**self.context_data())
        
        return "\n\n".join(self._context_data['body'])

    def save(self, file_path):
        try:
            os.makedirs(os.path.dirname(file_path))
        except Exception:
            pass
        with open(file_path, 'w+', encoding='utf-8') as static_file:
            static_file.writelines(self.generate())

###############################################################################
# Readme
###############################################################################
class Readme:
    def __init__(self, file_name='README.md', body=None, template_file='readme.tmpl', context_data=None, configuration=None, specifications=None, attributes=None):
        self.file_name = file_name
        self.template_file = os.path.join(TEMPLATE_DIR, template_file)
        self._context_data = context_data if context_data else {}
        self._context_data['body'] = [body] if body else []
        self._context_data['configuration'] = [configuration] if configuration else []
        self._context_data['specifications'] = [specifications] if specifications else []
        self._context_data['attributes'] = [attributes] if attributes else []

    def __add__(self, other):
        for code in other._context_data['body']:
            if code not in self._context_data['body']:
                self._context_data['body'].append(code)
        for code in other._context_data['configuration']:
            if code not in self._context_data['configuration']:
                self._context_data['configuration'].append(code)
        for code in other._context_data['specifications']:
            if code not in self._context_data['specifications']:
                self._context_data['specifications'].append(code)
        for code in other._context_data['attributes']:
            if code not in self._context_data['attributes']:
                self._context_data['attributes'].append(code)
        return self

    def context_data(self):
        data = self._context_data
        data['body'] = "\n\n".join(self._context_data['body'])
        data['configuration'] = "\n\n".join(self._context_data['configuration'])
        data['specifications'] = "\n\n".join(self._context_data['specifications'])
        data['attributes'] = "\n\n".join(self._context_data['attributes'])
        return self._context_data

    def generate(self):
        with open(self.template_file, 'rb') as tmpl:
            template = tmpl.read().decode('utf-8')
        return template.format(**self.context_data())

    def save(self, file_path):
        try:
            os.makedirs(os.path.dirname(file_path))
        except Exception:
            pass
        with open(file_path, 'w+', encoding='utf-8') as static_file:
            static_file.writelines(self.generate())

###############################################################################
# GraphQl
###############################################################################
class GraphQlSchema:
    def __init__(self):
        self.object_types = []
    
    def __add__(self, other):
        for object_type in other.object_types:
            self.add_objecttype(object_type)
        return self
        
    def add_objecttype(self, object_type):
        if object_type in self.object_types:
            index = self.object_types.index(object_type)
            self.object_types[index] = self.object_types[index] + object_type
        else:
            self.object_types.append(object_type)
            
    def generate(self):
        object_types = '\n\n'.join(t.generate() for t in self.object_types)
        return TemplateEngine.render('graphql/schema_core.j2', {'object_types': object_types})
        
    def save(self, path):
        try:
            os.makedirs(os.path.dirname(path))
        except Exception:
            pass
        with open(path, 'w+', encoding='utf-8') as f:
            f.write(self.generate())

class GraphQlObjectType:
    def __init__(self, type, **kwargs):
        self.type = type
        self.type_declaration = kwargs.get('type_declaration', 'type')
        self.body = [kwargs.get('body', '')]
        self.object_items = []
        
    def __eq__(self, other):
        return self.type == other.type
        
    def __add__(self, other):
        for item in other.object_items:
            self.add_objectitem(item)
        for code in other.body:
            if code not in self.body:
                self.body.append(code)
        return self
        
    def add_objectitem(self, object_item):
        if object_item in self.object_items:
            index = self.object_items.index(object_item)
            self.object_items[index] = self.object_items[index] + object_item
        else:
            self.object_items.append(object_item)
            
    def generate(self):
        object_items = '\n'.join(i.generate() for i in self.object_items)
        body_str = '\n'.join(self.body)
        return TemplateEngine.render('graphql/object.j2', {
            'type_declaration': self.type_declaration,
            'type': self.type,
            'object_items': object_items,
            'body': body_str
        })
    
    def save(self, path):
        pass

class GraphQlObjectItem:
    def __init__(self, item_identifier, **kwargs):
        self.item_identifier = item_identifier
        self.item_type = kwargs.get('item_type', 'String')
        self.base_type = kwargs.get('base_type', '')
        self.item_arguments = kwargs.get('item_arguments', '')
        self.item_resolver = kwargs.get('item_resolver', '')
        self.item_description = kwargs.get('description', '')
        self.item_cache_identity = kwargs.get('item_cache_identity', '')
        self.body = [kwargs.get('body', '')]
        
        # Process Decorators
        if self.item_description:
            desc = self.item_description
            if self.base_type == 'Mutation':
                self.item_description = f'@doc(description: "Input {desc}.")'
            else:
                self.item_description = f'@doc(description: "Query by {desc}.")'
                
        if self.item_resolver:
            self.item_resolver = f'@resolver(class: "{self.item_resolver}")'
            
        if self.item_cache_identity:
            self.item_cache_identity = f'@cache(cacheIdentity: "{self.item_cache_identity}")'
            
        if self.item_arguments and ',' in self.item_arguments:
            args = []
            for arg in self.item_arguments.split(','):
                args.append(f'{arg}: String')
            self.item_arguments = '(\n' + ",\n".join(args) + '\n)'
            
    def __eq__(self, other):
        return self.item_identifier == other.item_identifier
        
    def __add__(self, other):
        return self
        
    def generate(self):
        return TemplateEngine.render('graphql/item.j2', {
            'item_identifier': self.item_identifier,
            'item_arguments': self.item_arguments,
            'item_type': self.item_type,
            'item_resolver': self.item_resolver,
            'item_description': self.item_description,
            'item_cache_identity': self.item_cache_identity,
            'body': "\n".join(self.body)
        })

###############################################################################
# Module
###############################################################################
class Module:
    def __init__(self, package, name, description='', license=None):
        if not package or not name:
            raise ValueError("Package and Module name cannot be empty.")
            
        self.package = upperfirst(package)
        self.name = upperfirst(name)
        self.description = description
        self.license = license
        self._graphqlschemas = {}
        self._xmls = {}
        self._classes = {}
        self._static_files = {}
        
        # Default module.xml
        etc_module = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:Module/etc/module.xsd"}, nodes=[Xmlnode('module', attributes={'name': self.module_name})])
        self.add_xml('etc/module.xml', etc_module)
        
        composer_name = '{}/module-{}'.format(self.package.lower(), self.name.lower())
        self.add_static_file('.', Readme(context_data={'package_name': upperfirst(self.package), 'name': upperfirst(self.name), 'module_name': self.module_name, 'composer_name': composer_name, 'description': self.description}))
        
        self._composer = OrderedDict()
        self._composer['name'] = composer_name
        self._composer['description'] = self.description
        self._composer['type'] = 'magento2-module'
        self._composer['license'] = 'proprietary'
        self._composer['authors'] = [{'name': self.package, 'email': 'info@example.com'}]
        self._composer['minimum-stability'] = 'dev'
        self._composer['require'] = {"php": "~7.4.0||~8.1.0||~8.2.0||~8.3.0", "magento/framework": "*"}
        self._composer['autoload'] = {'files': ['registration.php'], 'psr-4': {"{}\\{}\\".format(self.package, self.name): ""}}

    @property
    def module_name(self):
        return '{}_{}'.format(self.package, self.name)

    @classmethod
    def load_module(cls, data):
        return cls('Experius', 'Test')

    def generate_module(self, root_location):
        if not os.path.exists(root_location):
            raise Exception('Location does not exists')
        location = os.path.join(root_location, self.package, self.name)
        try:
            os.makedirs(location)
        except Exception:
            pass
            
        context_data = {'module_name': self.module_name, 'license': ''}
        if self.license:
            self._composer['license'] = self.license.identifier
            self.add_static_file('', StaticFile('LICENSE.txt', body=self.license.get_text()))
            self.add_static_file('', StaticFile('COPYING.txt', body=self.license.get_short_text()))
            context_data = {'module_name': self.module_name, 'license': self.license.get_php_docstring()}
            
        # Generate Registration
        registration_content = TemplateEngine.render('registration.j2', context_data)
        self.add_static_file('.', StaticFile('registration.php', body=registration_content))
        
        # Save Classes
        for class_name, phpclass in self._classes.items():
            phpclass.save(root_location)
            
        # Save GraphQL Schemas
        for graphqlschema_file, graphqlobjecttype in self._graphqlschemas.items():
            path = os.path.join(location, graphqlschema_file)
            graphqlobjecttype.save(path)
            
        # Save XML files
        for xml_file, node in self._xmls.items():
            path = os.path.join(location, xml_file)
            node.save(path)
            
        # Save Static Files
        for path, static_file in self._static_files.items():
            path = os.path.join(location, path)
            static_file.save(path)
            
        # [FIX] Save composer.json
        with open(os.path.join(location, 'composer.json'), 'w+', encoding='utf-8') as f:
            json.dump(self._composer, f, indent=4)

    def add_composer_require(self, require, version = "*", dev = False):
        if dev:
            if 'require-dev' not in self._composer:
                self._composer['require-dev'] = {}
            self._composer['require-dev'][require] = version
        else:
            self._composer['require'][require] = version

    def add_class(self, phpclass):
        root_namespace = r'{}\{}'.format(self.package, self.name)
        if root_namespace not in phpclass.class_namespace:
            phpclass.class_namespace = r'{}\{}'.format(root_namespace, phpclass.class_namespace)
        current_class = self._classes.get(phpclass.class_namespace)
        if current_class:
            current_class += phpclass
        else:
            current_class = phpclass
        current_class.license = self.license
        self._classes[current_class.class_namespace] = current_class

    def add_graphqlschema(self, graphqlschema_file, schema):
        current_schema = self._graphqlschemas.get(graphqlschema_file)
        if current_schema:
            current_schema += schema
        else:
            self._graphqlschemas[graphqlschema_file] = schema

    def add_xml(self, xml_file, node):
        current_xml = self._xmls.get(xml_file)
        if current_xml:
            # For module.xml, we need special merging logic to avoid duplicating sequence nodes
            if xml_file == 'etc/module.xml':
                self._merge_module_xml(current_xml, node)
            else:
                if current_xml != node:
                    raise Exception('Cant merge XML nodes root node must be the same')
                current_xml.add_nodes(node.nodes)
        else:
            self._xmls[xml_file] = node

    def _merge_module_xml(self, current, new_node):
        """Helper to merge module.xml sequence nodes cleanly"""
        # Find sequence node in current
        curr_seq = None
        for child in current.nodes[0].nodes: # config -> module -> children
            if child.node_name == 'sequence':
                curr_seq = child
                break
        
        # Find sequence node in new
        new_seq = None
        for child in new_node.nodes[0].nodes:
            if child.node_name == 'sequence':
                new_seq = child
                break
        
        if new_seq:
            if not curr_seq:
                current.nodes[0].nodes.append(new_seq)
            else:
                curr_seq.add_nodes(new_seq.nodes)

    def add_static_file(self, path, staticfile):
        full_name = os.path.join(path, staticfile.file_name)
        current_staticfile = self._static_files.get(full_name)
        if current_staticfile:
            current_staticfile += staticfile
        else:
            current_staticfile = staticfile
        self._static_files[full_name] = current_staticfile
