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
from proposing.models import Proposal, Comment, ProxyProposalVote, Tag, Proxy
from decorators import not_logged_in
from forms import CustomUserCreationForm, ProfileUpdateForm, EmailAuthenticationForm
from models import CustomUser
from django.db.models.aggregates import Count

def getuserproposals(member):
    return Proposal.objects.filter(creator=member)
     
def getusercomments(member):
    return Comment.objects.filter(creator=member)

def getuserproxies(member):
    return Proxy.objects.filter(delegating=member).values('delegates').distinct()

def getuservotes(member):
    return ProxyProposalVote.objects.filter(user=member,voted_self=True)

def getuserproxyvotes(member):
    return ProxyProposalVote.objects.filter(user=member,voted_self=False)

def getparticipatedproposals(member):
    return (Proposal.objects.filter(creator=member) | 
                 Proposal.objects.filter(comments__creator=member) | 
                 Proposal.objects.filter(proposal_votes__user=member).exclude(voting_stage='VOTING') # don't leak votings in progress
                 ).distinct()

def getusertags(member):
    tag_id_list = getparticipatedproposals(member).values('tags').annotate(count=Count('tags')).distinct().order_by('-count')
    return [(Tag.objects.get(pk=item['tags']), item['count']) for item in tag_id_list]
    
def userprofile(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.addView()
    
    return render(request, 'accounts/profile.html', {
        'member': member,
        'proposal_list': getuserproposals(member),
        'comment_list': getusercomments(member),
        'tag_list': getusertags(member),
        'vote_list': getuservotes(member),
        'proxy_list': getuserproxies(member),    
        'proxy_vote_list': getuserproxyvotes(member),
    })


def userproposals(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.addView()
    
    return render(request, 'accounts/userproposals.html', {
        'member': member,
        'proposal_list': getuserproposals(member)    
    })

def usercomments(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.addView()
    
    return render(request, 'accounts/usercomments.html', {
        'member': member,
        'comment_list': getusercomments(member),    
    })

def usertags(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.addView()
    
    return render(request, 'accounts/usertags.html', {
        'member': member,
        'tag_list': getusertags(member),    
    })

def uservotes(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.addView()
    
    return render(request, 'accounts/uservotes.html', {
        'member': member,
        'vote_list': getuservotes(member),    
    })

def userproxyvotes(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.addView()
    
    return render(request, 'accounts/userproxyvotes.html', {
        'member': member,
        'proxy_vote_list': getuserproxyvotes(member),
    })

def userproxies(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.addView()
    
    return render(request, 'accounts/userproxies.html', {
        'member': member,
        'proxy_list': getuserproxies(member),    
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
    
