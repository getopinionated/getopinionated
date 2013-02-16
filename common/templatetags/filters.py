from django import template
from common.stringify import niceBigInteger


register = template.Library()

@register.filter(name='smallint')
def smallint(value):
    return niceBigInteger(value,smallest=True)

@register.filter(name='mediumint')
def mediumint(value):
    return niceBigInteger(value)
