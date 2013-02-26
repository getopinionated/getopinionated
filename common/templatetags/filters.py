from django import template
from common.stringify import niceBigInteger,timesince
from common.htmldiff import htmldiff
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='smallint')
def smallint(value):
    return niceBigInteger(value,smallest=True)

@register.filter(name='mediumint')
def mediumint(value):
    return niceBigInteger(value)

@register.filter(name='humantime')
def humantime(value):
    return timesince(value)

@register.filter(name='shorttime')
def shorttime(value):
    return timesince(value, onepart=True)

@register.filter(name='diffrender',is_safe=True)
def diffrender(diff, contextlines=3):
    return mark_safe(htmldiff(diff.getOriginalText(), diff.getNewText(), addStylesheet=True))