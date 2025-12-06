from .. import Snippet, StaticFile, Readme, Xmlnode
from ..core.template import TemplateEngine
from ..utils import upperfirst

class CronjobSnippet(Snippet):
    snippet_label = 'Cronjob'
    description = "Create a Cron Job."

    def add(self, name, schedule="*/5 * * * *", group="default", **kwargs):
        package = self._module.package
        module = self._module.name
        class_name = upperfirst(name)
        namespace = f"{package}\\{module}\\Cron"

        # PHP
        content = TemplateEngine.render('snippets/cron/cronjob.j2', {
            'namespace': namespace,
            'class_name': class_name
        })
        self.add_static_file("Cron", StaticFile(f"{class_name}.php", body=content))

        # XML
        job_name = f"{package.lower()}_{module.lower()}_{name.lower()}"
        config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Cron:etc/crontab.xsd"}, nodes=[
            Xmlnode('group', attributes={'id': group}, nodes=[
                Xmlnode('job', attributes={
                    'name': job_name,
                    'instance': f"{namespace}\\{class_name}",
                    'method': 'execute'
                }, nodes=[
                    Xmlnode('schedule', node_text=schedule)
                ])
            ])
        ])
        self.add_xml('etc/crontab.xml', config)

        self.add_static_file('.', Readme(specifications=f" - Cron: {job_name} ({schedule})"))