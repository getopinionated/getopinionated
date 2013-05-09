#!/usr/bin/env python

from django.contrib.auth import authenticate
from django.contrib.auth.views import login, logout
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from common.shortcuts import render_to_response
from proposing.models import Proposal, Comment, ProxyProposalVote, Tag
from decorators import not_logged_in
from forms import CustomUserCreationForm, ProfileUpdateForm, EmailAuthenticationForm
from models import CustomUser
from django.db.models.aggregates import Count

def userprofile(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.addView()
    proposal_list = Proposal.objects.filter(creator=member)
    comment_list = Comment.objects.filter(creator=member)
    vote_list = ProxyProposalVote.objects.filter(user=member,voted_self=True)
    proxy_list = ProxyProposalVote.objects.filter(user=member,voted_self=False)
    
    prop_list = (proposal_list.all() | 
                 Proposal.objects.filter(comments__creator=member)).distinct()
    tag_id_list = prop_list.values('tags').annotate(count=Count('tags')).distinct().order_by('-count')
    tag_list = [(Tag.objects.get(pk=item['tags']), item['count']) for item in tag_id_list]
        
    return render(request, 'accounts/profile.html', {
        'member': member,
        'proposal_list': proposal_list,
        'comment_list': comment_list,
        'tag_list': tag_list,
        'vote_list': vote_list,
        'proxy_list': proxy_list,        
    })

@not_logged_in
def userlogin(request):
    return login(request,
        authentication_form=EmailAuthenticationForm,
        template_name='accounts/login.html',
    )


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
    return logout(request, next_page='/')
    
