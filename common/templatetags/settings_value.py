from django import template
from django.conf import settings
from django.template.base import TemplateSyntaxError

register = template.Library()

@register.simple_tag
def settings_value(name):
    """ get settings value """
    val = getattr(settings, name, None)
    if val == None and settings.DEBUG:
        raise TemplateSyntaxError('Unknown settings value "{}" in {{% settings_value %}}'.format(name, name))
    return val
