# mage2gen/snippets/schemapatch.py
import os
from .. import Phpclass, Phpmethod, StaticFile, Snippet, SnippetParam, Readme
from ..module import TEMPLATE_DIR

class SchemaPatchSnippet(Snippet):
    snippet_label = 'Schema Patch'
    description = "Create a Schema Patch for safe database migrations (renaming tables, columns, etc)."

    OPERATIONS = [
        ('custom', 'Custom'),
        ('rename_table', 'Rename Table'),
        ('rename_column', 'Rename Column'),
    ]

    def add(self, patch_name, operation='custom', table_name='', old_name='', new_name='', extra_params=None):
        
        patch_class_name = 'Setup\\Patch\\Schema\\' + patch_name
        
        # Determine Body Logic
        body = "// Add your schema modification logic here"
        
        if operation == 'rename_table':
            if not old_name or not new_name:
                raise Exception("Old Name and New Name are required for rename_table")
            body = """        $connection->renameTable(
            $this->schemaSetup->getTable('{}'),
            $this->schemaSetup->getTable('{}')
        );""".format(old_name, new_name)
            
        elif operation == 'rename_column':
            if not table_name or not old_name or not new_name:
                raise Exception("Table Name, Old Name, and New Name are required for rename_column")
            body = """        $connection->changeColumn(
            $this->schemaSetup->getTable('{}'),
            '{}',
            '{}',
            [
                'type' => \Magento\Framework\DB\Ddl\Table::TYPE_TEXT, // TODO: Check Type
                'length' => 255,
                'comment' => 'Renamed Column'
            ]
        );""".format(table_name, old_name, new_name)

        # Create PHP Class using Module's template system manually or constructing Phpclass
        # Since we have a specific template for structure, we can use StaticFile or generic Phpclass
        # Using Phpclass is better for dependency management, but we created a custom template.
        # Let's adapt Phpclass to use our custom template for the body? 
        # Actually, standard Phpclass is flexible enough if we put the body in the method.
        
        # Let's use standard Phpclass construction to be consistent with other snippets
        patch_class = Phpclass(
            patch_class_name,
            implements=['SchemaPatchInterface'],
            dependencies=[
                'Magento\\Framework\\Setup\\Patch\\SchemaPatchInterface',
                'Magento\\Framework\\Setup\\SchemaSetupInterface'
            ],
            attributes=[
                '/**\n     * @var SchemaSetupInterface\n     */',
                'private $schemaSetup;'
            ]
        )
        
        patch_class.add_method(Phpmethod(
            '__construct',
            params=['SchemaSetupInterface $schemaSetup'],
            body='$this->schemaSetup = $schemaSetup;',
            docstring=['Constructor', '@param SchemaSetupInterface $schemaSetup']
        ))
        
        patch_class.add_method(Phpmethod(
            'apply',
            body="""$this->schemaSetup->startSetup();
$connection = $this->schemaSetup->getConnection();

{}

$this->schemaSetup->endSetup();""".format(body),
            docstring=['{@inheritdoc}']
        ))
        
        # Boilerplate methods
        patch_class.add_method(Phpmethod('getDependencies', return_type='array', body='return [];', docstring=['{@inheritdoc}']))
        patch_class.add_method(Phpmethod('getAliases', return_type='array', body='return [];', docstring=['{@inheritdoc}']))

        self.add_class(patch_class)
        
        self.add_static_file('.', Readme(specifications=" - Schema Patch\n\t- {}".format(patch_class_name)))

    @classmethod
    def params(cls):
        return [
            SnippetParam('patch_name', required=True, description='e.g. RenameBlogTable'),
            SnippetParam('operation', choises=cls.OPERATIONS, default='custom'),
            SnippetParam('table_name', description='Required for column operations', depend={'operation': 'rename_column'}),
            SnippetParam('old_name', description='Old table/column name', depend={'operation': r'rename_table|rename_column'}),
            SnippetParam('new_name', description='New table/column name', depend={'operation': r'rename_table|rename_column'}),
        ]