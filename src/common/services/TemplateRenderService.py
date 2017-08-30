import re
from bottle import jinja2_template as template

field_variables_pattern = re.compile('{{.+?}}', re.MULTILINE)


def render_content(template_contents, data: dict):
    return template(template_contents, data)


def render_field(field, data: dict):
    if field_variables_pattern.search(field) is None:
        return field
    else:
        return render_content(field, data)
