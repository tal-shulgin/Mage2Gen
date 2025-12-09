import os
from .. import Snippet, StaticFile, Readme
from ..core.template import TemplateEngine
from ..utils import upperfirst, to_pascal_case

class IntegrationTestSnippet(Snippet):
    snippet_label = 'Integration Test'
    description = "Create a database-backed Integration Test for a Repository."

    def add(self, repository, data_interface, test_field=None, **kwargs):
        package = self._module.package
        module = self._module.name
        
        repo_short = repository.split('\\')[-1]
        data_interface_short = data_interface.split('\\')[-1]
        
        class_name = f"{repo_short}Test"
        namespace = f"{package}\\{module}\\Test\\Integration\\Model"
        
        test_field_setter = ""
        test_field_getter = ""
        if test_field:
            camel = to_pascal_case(test_field)
            test_field_setter = f"set{camel}"
            test_field_getter = f"get{camel}"

        content = TemplateEngine.render('snippets/test/integration/crud.j2', {
            'namespace': namespace,
            'class_name': class_name,
            'repository_interface': repository,
            'repository_short': repo_short,
            'data_interface': data_interface,
            'data_interface_short': data_interface_short,
            'test_field_setter': test_field_setter,
            'test_field_getter': test_field_getter
        })

        self.add_static_file(f"Test/Integration/Model", StaticFile(f"{class_name}.php", body=content))
        self.add_static_file('.', Readme(specifications=f" - Integration Test: {class_name}"))