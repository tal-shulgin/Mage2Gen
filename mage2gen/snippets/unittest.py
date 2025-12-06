from .. import Snippet, StaticFile, Readme
from ..core.template import TemplateEngine
from ..utils import upperfirst

class UnitTestSnippet(Snippet):
    snippet_label = 'Unit Test'
    description = "Create a PHPUnit Test Case."

    def add(self, test_suite, test_name, **kwargs):
        package = self._module.package
        module = self._module.name
        
        class_name = f"{upperfirst(test_suite)}Test"
        namespace = f"{package}\\{module}\\Test\\Unit"
        
        content = TemplateEngine.render('snippets/unittest/test.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'test_method': upperfirst(test_name)
        })
        self.add_static_file(f"Test/Unit/{class_name}", StaticFile(f"{class_name}.php", body=content))

        self.add_static_file('.', Readme(specifications=f" - Unit Test: {class_name}"))