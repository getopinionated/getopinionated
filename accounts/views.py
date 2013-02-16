#!/usr/bin/env python

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from common.shortcuts import render_to_response
from decorators import not_logged_in
from forms import ProfileCreationForm, ProfileUpdateForm, EmailAuthenticationForm
from django.contrib.auth.models import User
from proposing.models import Proposal
from django.shortcuts import render, get_object_or_404

def userprofile(request, username):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(User,username=username)
    proposal_list = Proposal.objects.filter(creator=member)
    return render(request, 'accounts/profile.html', {
        'member': member,
        'proposal_list': proposal_list
    })

@not_logged_in
def userlogin(request):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    auth_form = EmailAuthenticationForm(None, request.POST or None)
    # The form itself handles authentication and checking to make sure password and such are supplied.
    if auth_form.is_valid():
        login(request, auth_form.get_user())
        return HttpResponseRedirect(reverse('home-index'))
 
    return render_to_response(request, 'accounts/login.html', {
        'form': auth_form,
    })

@not_logged_in
def userregister(request):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    if request.method == 'POST':
        form = ProfileCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            new_user = authenticate(username=user.username,
                                    password=request.POST['password1'])
            login(request, new_user)
            messages.success(request, 'Registration complete')
            return HttpResponseRedirect(reverse('profile-update'))
    else:
        form = ProfileCreationForm()

    return render_to_response(request, 'accounts/register.html', {
        'form': form,
    })

@login_required
def profileupdate(request):
        # Initialize the form either fresh or with the appropriate POST data as the instance
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile details updated')
            return HttpResponseRedirect(reverse('profile-update'))
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render_to_response(request, 'accounts/update.html', {
        'form': form,
    })

@login_required
def userlogout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home-index'))
