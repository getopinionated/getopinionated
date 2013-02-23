from django import template
from common.stringify import niceBigInteger,timesince


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
