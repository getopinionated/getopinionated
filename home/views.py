#!/usr/bin/env python
# author: Jens Nyman (nymanjens.nj@gmail.com)

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from common.shortcuts import render_to_response

def index(request):
    return render_to_response(request, 'home/index.html', {})


