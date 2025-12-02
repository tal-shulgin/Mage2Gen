import os
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme

class InstallSnippet(Snippet):
    snippet_label = 'Data Patch'
    description = "Creates a Data Patch class for Magento 2.4+."

    def add(self, patch_name, extra_params=None):
        patch_class_name = 'Setup\\Patch\\Data\\' + patch_name
        patch_class = Phpclass(
            patch_class_name,
            implements=['DataPatchInterface'],
            dependencies=[
                'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
                'Magento\\Framework\\Setup\\ModuleDataSetupInterface'
            ],
            attributes=['/** @var ModuleDataSetupInterface */', 'private $moduleDataSetup;']
        )
        patch_class.add_method(Phpmethod(
            '__construct',
            params=['ModuleDataSetupInterface $moduleDataSetup'],
            body='$this->moduleDataSetup = $moduleDataSetup;',
            docstring=['Constructor', '@param ModuleDataSetupInterface $moduleDataSetup']
        ))
        patch_class.add_method(Phpmethod(
            'apply',
            return_type='void',
            body='$this->moduleDataSetup->getConnection()->startSetup();\n\n// Your code here\n\n$this->moduleDataSetup->getConnection()->endSetup();',
            docstring=['{@inheritdoc}']
        ))
        patch_class.add_method(Phpmethod('getDependencies', access='public static', return_type='array', body='return [];', docstring=['{@inheritdoc}']))
        patch_class.add_method(Phpmethod('getAliases', return_type='array', body='return [];', docstring=['{@inheritdoc}']))

        self.add_class(patch_class)
        
        self.add_static_file('.', Readme(specifications=" - Data Patch\n\t- {}".format(patch_class_name)))

    @classmethod
    def params(cls):
        return [SnippetParam(name='patch_name', required=True, default='InitialData')]
