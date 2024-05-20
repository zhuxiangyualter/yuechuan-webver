from django import template
from django.template.defaultfilters import stringfilter
from markdown import Markdown
from io import StringIO

register = template.Library()

def unmark(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()

Markdown.output_formats['plain'] = unmark

md = Markdown(
    extensions=[
        'markdown.extensions.codehilite',
        'markdown.extensions.meta',
        'markdown.extensions.extra',
        'pymdownx.arithmatex'
    ],
    extension_configs={
        'pymdownx.arithmatex': {
            'generic': True
        }
    }
)

mu = Markdown(output_format='plain')
mu.stripTopLevelTags = False

@register.filter('markdown', is_safe=True)
@stringfilter
def render(value):
    return md.convert(value)

@register.filter('unmarkdown')
@stringfilter
def unmarkup(value):
    return mu.convert(value)