from jinja2 import Template


def render_content(contents, data: dict):
    return Template(contents).render(data)
