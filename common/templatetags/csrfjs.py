import re, random
from django import template
from django.utils.safestring import mark_safe
from django.template.defaulttags import CsrfTokenNode

register = template.Library()

class CsrfJsTokenNode(CsrfTokenNode):
    def render(self, context):
        csrf_token = context.get('csrf_token', None)
        if csrf_token:
            if csrf_token == 'NOTPROVIDED':
                return mark_safe(u"")
            else:
                token = u"<div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' /></div>"
                token += self.generateJavascriptCode(csrf_token)
                return mark_safe(token)
        else:
            # It's very probable that the token is missing because of
            # misconfiguration, so we raise a warning
            from django.conf import settings
            if settings.DEBUG:
                import warnings
                warnings.warn("A {% csrf_js_token %} was used in a template, but the context did not provide the value.  This is usually caused by not using RequestContext.")
            return u''

    def generateJavascriptCode(self, csrf_token):
        character_set = '+-.0123456789@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
        char_list = list(character_set)
        random.shuffle(char_list)
        key = ''.join(char_list)
        cipher_text = ''
        for a in csrf_token:
            cipher_text += key[ character_set.find(a) ]
        script =  'var a="'+key+'";var b=a.split("").sort().join("");var c="'+cipher_text+'";var d="";'
        script += 'for(var e=0;e<c.length;e++)d+=b.charAt(a.indexOf(c.charAt(e)));'
        script += '$("input[name=\'csrfmiddlewaretoken\']").val(d);'
        script = "eval(\""+ script.replace("\\","\\\\").replace('"','\\"') + "\")"
        script = '<script type="text/javascript">/*<![CDATA[*/'+script+'/*]]>*/</script>'
        return unicode(script)

def csrf_js_token(parser, token):
    """
        {% csrf_js_token %}
    """
    return CsrfJsTokenNode()

register.tag('csrf_js_token', csrf_js_token)
