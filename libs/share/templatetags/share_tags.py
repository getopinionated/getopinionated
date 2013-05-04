import urlparse
from django.template import Library, TemplateSyntaxError, Node
from django.utils.http import urlquote
from django.conf import settings
from share.settings import *
from django.template.loader import render_to_string

register = Library()

@register.simple_tag
def share_css():
    return "<link href='" + settings.STATIC_URL + "css/share.css' type='text/css' rel='stylesheet' />"

@register.simple_tag
def share_js():
    return "<script src='" + settings.STATIC_URL + "js/share.js' type='text/javascript'></script>"

class ShareNode(Node):
    def __init__(self, providers=None):
        self.providers = providers
    def render(self, context):
        return render_to_string('share/links.html', {'providers': self.providers, 'url': context['request'].build_absolute_uri()}, context_instance=context)

@register.tag
def share(parser, token):
    args = token.split_contents()

    if len(args) == 1:
        providers = SHARE_PROVIDERS
    else:
        args.pop(0)
        providers = args

    return ShareNode(providers)
