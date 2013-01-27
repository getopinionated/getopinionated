from django import template
from django.conf import settings
from django.template.defaultfilters import linebreaks


register = template.Library()

def custom_linebreaks(value):
    """ only do linebreak if it contains serious html code """
    serios_html = ["<li", "<br", "<ul", "<ol", "<p", "<div", '<table']
    for string in serios_html:
        if string in value:
            return value
    return linebreaks(value)

register.filter('custom_linebreaks', custom_linebreaks)
