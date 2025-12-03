# A Magento 2 module generator library
# Copyright (C) 2025 Mage2Gen
import os
from .. import StaticFile, Snippet, SnippetParam, Readme

class LessSnippet(Snippet):
    snippet_label = 'Less (CSS)'
    description = """
    Generates standard Less file structure for frontend styling.
    """

    def add(self, extra_params=None):
        # _module.less
        module_less_body = """//
//  {module_name}
//  _____________________________________________

& when (@media-common = true) {{
    .example-class {{
        // Styles common to all media queries
        color: @primary__color;
    }}
}}

.media-width(@extremum, @break) when (@extremum = 'min') and (@break = @screen__m) {{
    .example-class {{
        // Styles for desktop and larger
    }}
}}

.media-width(@extremum, @break) when (@extremum = 'max') and (@break = @screen__m) {{
    .example-class {{
        // Styles for mobile
    }}
}}
""".format(module_name=self.module_name)

        path = 'view/frontend/web/css/source'
        self.add_static_file(os.path.join(path, '_module.less'), StaticFile('_module.less', body=module_less_body))

        self.add_static_file(
            '.',
            Readme(
                specifications=" - Less\n\t- view/frontend/web/css/source/_module.less",
            )
        )

    @classmethod
    def params(cls):
        return []