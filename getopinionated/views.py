from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.conf import settings
import proposing.views

def home(request):
    if request.user.is_authenticated():
        return proposing.views.proplist(request)
    else:
        return about(request)

def about(request):
    about_template_filename = settings.ABOUT_PAGE_FILENAME
    return render(request, "about/{}".format(about_template_filename), {})

def under_maintenance(request):
    return render(request, "under_maintenance.html")