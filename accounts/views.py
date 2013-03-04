#!/usr/bin/env python

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from common.shortcuts import render_to_response
from proposing.models import Proposal
from decorators import not_logged_in
from forms import CustomUserCreationForm, ProfileUpdateForm, EmailAuthenticationForm
from models import CustomUser

def userprofile(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
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
def passwordreset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(email_template_name='accounts/password_reset_email.txt')
            messages.success(request, 'An email has been sent to the provided email address.')
            return HttpResponseRedirect(reverse('password-reset'))
    else:
        form = PasswordResetForm()
    return render_to_response(request, 'accounts/password-reset.html', {
        'form': form,
    })

@not_logged_in
def userregister(request):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            new_user = authenticate(username=user.username,
                                    password=request.POST['password1'])
            login(request, new_user)
            messages.success(request, 'Registration complete')
            return HttpResponseRedirect(reverse('profile-update'))
    else:
        form = CustomUserCreationForm()

    return render_to_response(request, 'accounts/register.html', {
        'form': form,
    })

@login_required
def profileupdate(request):
    ## profile update form
    if request.method == 'POST' and 'profileupdate' in request.POST:
        profileform = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        
        if profileform.is_valid():
            profileform.save()
            messages.success(request, 'Profile details updated')
            return HttpResponseRedirect(reverse('profile-update'))
    else:
        profileform = ProfileUpdateForm(instance=request.user)
    ## password change form
    if request.method == 'POST' and 'passwordchange' in request.POST:
        passwordform = PasswordChangeForm(request.user, request.POST)
        if passwordform.is_valid():
            passwordform.save()
            messages.success(request, 'Password changed')
            return HttpResponseRedirect(reverse('profile-update'))
    else:
        passwordform = PasswordChangeForm(request.user)

    return render_to_response(request, 'accounts/update.html', {
        'profileform': profileform,
        'passwordform': passwordform,
    })

@login_required
def userlogout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home-index'))
    
