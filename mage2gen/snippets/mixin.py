# A Magento 2 module generator library
# Copyright (C) 2025 Mage2Gen
import os
from .. import Module, StaticFile, Snippet, SnippetParam, Readme

class MixinSnippet(Snippet):
    snippet_label = 'JS Mixin'
    description = """
    Create a JS Mixin to extend or modify a core Magento JS component or a third-party JS component.
    """

    SCOPE_FRONTEND = 'frontend'
    SCOPE_ADMINHTML = 'adminhtml'
    SCOPE_BASE = 'base'

    SCOPE_CHOISES = [
        (SCOPE_FRONTEND, 'Frontend'),
        (SCOPE_ADMINHTML, 'Adminhtml'),
        (SCOPE_BASE, 'Base'),
    ]

    def add(self, target_js, mixin_name=None, scope=SCOPE_FRONTEND, extra_params=None):
        if not mixin_name:
            mixin_name = target_js.replace('/', '_').replace('.', '_') + '_Mixin'

        # Cleanup mixin name for filename
        mixin_filename = mixin_name.replace('_', '/')
        
        mixin_path = '{}/js/{}'.format(self.module_name, mixin_filename)
        
        # 1. Create the Mixin JS file
        js_body = """define([], function () {
    'use strict';

    return function (target) {
        return target.extend({
            initialize: function () {
                this._super();
                // Add your custom logic here
                console.log('Mixin loaded for: %s');
            }
        });
    };
});
""".format(target_js)

        file_path = os.path.join('view', scope, 'web', 'js', '{}.js'.format(mixin_filename))
        self.add_static_file(file_path, StaticFile(os.path.basename(file_path), body=js_body))

        # 2. Add to requirejs-config.js
        requirejs_body = """
var config = {
    config: {
        mixins: {
            '%s': {
                '%s': true
            }
        }
    }
};
""".format(target_js, mixin_path)

        requirejs_path = os.path.join('view', scope, 'requirejs-config.js')
        self.add_static_file(requirejs_path, StaticFile('requirejs-config.js', body=requirejs_body))

        self.add_static_file(
            '.',
            Readme(
                specifications=" - JS Mixin\n\t- {} -> {}".format(mixin_path, target_js),
            )
        )

    @classmethod
    def params(cls):
        return [
            SnippetParam(
                name='target_js',
                required=True,
                description='The JS component to mix into (e.g., Magento_Checkout/js/view/shipping)',
                regex_validator=r'^[\w\/\.\-]+$',
                error_message='Invalid JS path format.'
            ),
            SnippetParam(
                name='mixin_name',
                required=False,
                description='Name for your mixin file (optional)',
                regex_validator=r'^[\w]+$',
                error_message='Only alphanumeric and underscores.'
            ),
            SnippetParam(
                name='scope',
                choises=cls.SCOPE_CHOISES,
                default=cls.SCOPE_FRONTEND
            )
        ]