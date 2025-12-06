import os
from jinja2 import Environment, PackageLoader, select_autoescape

class TemplateEngine:
    _env = None

    @classmethod
    def get_env(cls):
        if cls._env is None:
            cls._env = Environment(
                loader=PackageLoader('mage2gen', 'templates'),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
        return cls._env

    @classmethod
    def render(cls, template_name, context=None):
        """
        Render a Jinja2 template.
        
        Args:
            template_name (str): Path relative to templates/ folder (e.g. 'class.j2')
            context (dict): Data to pass to template
        """
        if context is None:
            context = {}
            
        template = cls.get_env().get_template(template_name)
        return template.render(**context)