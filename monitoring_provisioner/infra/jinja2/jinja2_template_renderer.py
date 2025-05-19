from monitoring_provisioner.service.i_template_renderer.template_renderer import ITemplateRenderer


class Jinja2TemplateRenderer(ITemplateRenderer):
    """
    A class to render Jinja2 templates with a given context.
    """

    def __init__(self, template_path: str):
        pass

    def render(self) -> str:
        pass