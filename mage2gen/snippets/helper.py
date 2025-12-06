from .. import Snippet, StaticFile, Readme
from ..core.template import TemplateEngine
from ..utils import upperfirst

class HelperSnippet(Snippet):
    snippet_label = 'Helper'
    description = "Create a generic Helper class."

    def add(self, name, **kwargs):
        package = self._module.package
        module = self._module.name
        class_name = upperfirst(name)
        namespace = f"{package}\\{module}\\Helper"

        content = TemplateEngine.render('snippets/helper/helper.j2', {
            'namespace': namespace,
            'class_name': class_name
        })
        self.add_static_file(f"Helper/{class_name}", StaticFile(f"{class_name}.php", body=content))
        self.add_static_file('.', Readme(specifications=f" - Helper: {class_name}"))