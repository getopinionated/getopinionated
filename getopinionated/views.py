from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

def home(request):
    return render(request, 'flatpages/home.html', {
    })