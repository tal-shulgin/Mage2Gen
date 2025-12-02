# A Magento 2 module generator library
# Copyright (C) 2025 Mage2Gen
#
# This file is part of Mage2Gen.
#
# Mage2Gen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import os
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme

class InstallSnippet(Snippet):
    snippet_label = 'Data Patch'
    description = """
    Creates a Data Patch class for Magento 2.4+.
    
    Data Patches replace the legacy InstallData and UpgradeData scripts. 
    They ensure that data modifications are applied only once and in a specific order.
    
    This snippet generates a class implementing \Magento\Framework\Setup\Patch\DataPatchInterface.
    """

    def add(self, patch_name, extra_params=None):
        patch_class_name = 'Setup\\Patch\\Data\\' + patch_name
        
        # Define the Patch Class
        patch_class = Phpclass(
            patch_class_name,
            implements=['DataPatchInterface'],
            dependencies=[
                'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
                'Magento\\Framework\\Setup\\ModuleDataSetupInterface'
            ],
            attributes=[
                '/** @var ModuleDataSetupInterface */',
                'private $moduleDataSetup;'
            ]
        )

        # Constructor
        patch_class.add_method(Phpmethod(
            '__construct',
            params=['ModuleDataSetupInterface $moduleDataSetup'],
            body='$this->moduleDataSetup = $moduleDataSetup;',
            docstring=[
                'Constructor',
                '',
                '@param ModuleDataSetupInterface $moduleDataSetup'
            ]
        ))

        # Apply Method
        patch_class.add_method(Phpmethod(
            'apply',
            return_type='void',
            body="""$this->moduleDataSetup->getConnection()->startSetup();

// Your code here (e.g. add EAV attributes, config settings, CMS blocks)

$this->moduleDataSetup->getConnection()->endSetup();""",
            docstring=['{@inheritdoc}']
        ))

        # GetDependencies Method
        patch_class.add_method(Phpmethod(
            'getDependencies',
            access='public static',
            return_type='array',
            body='return [];',
            docstring=['{@inheritdoc}']
        ))

        # GetAliases Method
        patch_class.add_method(Phpmethod(
            'getAliases',
            return_type='array',
            body='return [];',
            docstring=['{@inheritdoc}']
        ))

        self.add_class(patch_class)
        
        self.add_static_file(
            '.',
            Readme(
                specifications=" - Data Patch\n\t- {}".format(patch_class_name),
            )
        )

    @classmethod
    def params(cls):
        return [
            SnippetParam(
                name='patch_name',
                required=True,
                default='InitialData',
                description='Name of the patch class (e.g. AddDefaultProducts, UpdateConfig)',
                regex_validator=r'^[a-zA-Z0-9]+$',
                error_message='Only alphanumeric characters are allowed.'
            )
        ]