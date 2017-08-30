import re
from bottle import jinja2_template as template

containing_variables_pattern = re.compile('{{.+?}}', re.MULTILINE)


def render_content(contents, data: dict):
    if containing_variables_pattern.search(contents) is None:
        return contents
    else:
        return template(contents, data)
