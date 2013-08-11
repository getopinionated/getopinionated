from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import proposing.views

def home(request):
    if request.user.is_authenticated():
        return proposing.views.proplist(request)
    else:
        return render(request, 'flatpages/about.html', {
        })


def about(request):
    return render(request, 'flatpages/about.html', {
    })