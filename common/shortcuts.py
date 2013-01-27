#!/usr/bin/env python
# author: Jens Nyman (nymanjens.nj@gmail.com)

from django.shortcuts import render_to_response as real_render_to_response
from django.template.context import RequestContext


def render_to_response(request, template, data = None):
    # create response
    response = real_render_to_response(template, data, context_instance = RequestContext(request))
    # return response
    return response


