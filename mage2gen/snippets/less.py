import os
from .. import StaticFile, Snippet, SnippetParam, Readme
from ..core.template import TemplateEngine

class LessSnippet(Snippet):
    snippet_label = 'Less (CSS)'
    description = "Generates standard Less file structure for frontend styling."

    def add(self, extra_params=None):
        content = TemplateEngine.render('snippets/less/module.j2', {
            'module_name': self.module_name
        })

        path = 'view/frontend/web/css/source'
        self.add_static_file(os.path.join(path, '_module.less'), StaticFile('_module.less', body=content))

        self.add_static_file('.', Readme(specifications=" - Less\n\t- view/frontend/web/css/source/_module.less"))