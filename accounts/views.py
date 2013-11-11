#!/usr/bin/env python

from django.contrib.auth import authenticate
from django.contrib.auth.views import login, logout, auth_login
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import HttpResponseRedirect, render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count, Sum

from proposing.models import Proposal, Comment, FinalProposalVote, Tag, Proxy
from decorators import not_logged_in
from forms import CustomUserCreationForm, ProfileUpdateForm, EmailAuthenticationForm, SingleProxyForm
from models import UnsubscribeCode, CustomUser, LoginCode
from django.contrib.auth import load_backend
from django.conf import settings

def sort_by_popularity(votableposts):
    return sorted(votableposts, key=lambda vp: -vp.popularity)

def getuserproposals(member):
    items = Proposal.objects.filter(creator=member)
    return sort_by_popularity(items)

def getpositiveusercomments(member):
    items = Comment.objects.filter(creator=member, color='POS')
    return sort_by_popularity(items)

def getnegativeusercomments(member):
    items = Comment.objects.filter(creator=member, color='NEG')
    return sort_by_popularity(items)

def getneutralusercomments(member):
    items = Comment.objects.filter(creator=member, color='NEUTR')
    return sort_by_popularity(items)

def getuserproxies(member):
    return Proxy.objects.filter(delegating=member).values('delegates').distinct()

def getpositiveuservotes(member):
    return FinalProposalVote.objects.filter(user=member,voted_self=True).filter(value__gt=1)

def getneutraluservotes(member):
    return FinalProposalVote.objects.filter(user=member,voted_self=True).exclude(value__gt=1).exclude(value__lt=-1)

def getnegativeuservotes(member):
    return FinalProposalVote.objects.filter(user=member,voted_self=True).filter(value__lt=-1)

def getpositiveuserproxyvotes(member):
    return FinalProposalVote.objects.filter(user=member,voted_self=False).filter(value__gt=1)

def getneutraluserproxyvotes(member):
    return FinalProposalVote.objects.filter(user=member,voted_self=False).exclude(value__gt=1).exclude(value__lt=-1)

def getnegativeuserproxyvotes(member):
    return FinalProposalVote.objects.filter(user=member,voted_self=False).filter(value__lt=-1)

def getparticipatedproposals(member):
    return (Proposal.objects.filter(creator=member) |
             Proposal.objects.filter(comments__creator=member) |
             Proposal.objects.filter(proposal_votes__user=member).exclude(voting_stage='VOTING') # don't leak votings in progress
             ).distinct('pk')

def getusertags(member):
    tag_id_list = getparticipatedproposals(member).values('tags').annotate(count=Count('tags')).distinct().order_by('-count')
    return [(Tag.objects.get(pk=item['tags']), item['count']) for item in tag_id_list]

def userprofile(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.incrementViewCounter()

    if request.user.is_authenticated() and not request.user.pk==member.pk:
        if request.method == 'POST':
            proxyform = SingleProxyForm(request.user, member, request.POST)
            if proxyform.is_valid():
                proxyform.save()
                messages.success(request, 'Proxies saved')
                return HttpResponseRedirect(request.build_absolute_uri())
        else:
            proxyform = SingleProxyForm(request.user, member)
    else:
        proxyform = None
    return render(request, 'accounts/profile.html', {
        'member': member,
        'proposal_list': getuserproposals(member),
        'pos_comment_list': getpositiveusercomments(member),
        'neutr_comment_list': getneutralusercomments(member),
        'neg_comment_list': getnegativeusercomments(member),
        'tag_list': getusertags(member),
        'pos_vote_list': getpositiveuservotes(member),
        'neutr_vote_list': getneutraluservotes(member),
        'neg_vote_list': getnegativeuservotes(member),
        'proxy_list': getuserproxies(member),
        'pos_proxy_vote_list': getpositiveuserproxyvotes(member),
        'neutr_proxy_vote_list': getneutraluserproxyvotes(member),
        'neg_proxy_vote_list': getnegativeuserproxyvotes(member),
        'proxyform': proxyform
    })


def userproposals(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.incrementViewCounter()

    return render(request, 'accounts/userproposals.html', {
        'member': member,
        'proposal_list': getuserproposals(member)
    })

def usercomments(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.incrementViewCounter()

    return render(request, 'accounts/usercomments.html', {
        'member': member,
        'pos_comment_list': getpositiveusercomments(member),
        'neutr_comment_list': getneutralusercomments(member),
        'neg_comment_list': getnegativeusercomments(member),
    })

def usertags(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.incrementViewCounter()

    return render(request, 'accounts/usertags.html', {
        'member': member,
        'tag_list': getusertags(member),
    })

def uservotes(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.incrementViewCounter()

    return render(request, 'accounts/uservotes.html', {
        'member': member,
        'pos_vote_list': getpositiveuservotes(member),
        'neutr_vote_list': getneutraluservotes(member),
        'neg_vote_list': getnegativeuservotes(member),
    })

def userproxyvotes(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.incrementViewCounter()

    return render(request, 'accounts/userproxyvotes.html', {
        'member': member,
        'pos_proxy_vote_list': getpositiveuserproxyvotes(member),
        'neutr_proxy_vote_list': getneutraluserproxyvotes(member),
        'neg_proxy_vote_list': getnegativeuserproxyvotes(member),
    })

def userproxies(request, userslug):
    # Initialize the form either fresh or with the appropriate POST data as the instance
    member = get_object_or_404(CustomUser, slug=userslug)
    member.incrementViewCounter()

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
    return render(request, 'accounts/password-reset.html', {
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
            auth_login(request, new_user)
            messages.success(request, 'Registration complete')
            return HttpResponseRedirect(reverse('profile-update'))
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {
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
        passwordform = SetPasswordForm(request.user, request.POST)
        if passwordform.is_valid():
            passwordform.save()
            messages.success(request, 'Password changed')
            return HttpResponseRedirect(reverse('profile-update') + '#body')
    else:
        passwordform = SetPasswordForm(request.user)

    return render(request, 'accounts/update.html', {
        'profileform': profileform,
        'passwordform': passwordform,
    })

@login_required
def userlogout(request):
    return logout(request, next_page='/')

def mailunsubscribe(request, code):
    unsubscribecode = UnsubscribeCode.objects.get(code=code)
    user = unsubscribecode.user
    user.weekly_digest = False
    user.daily_digest = False
    user.save()
    return render(request, 'accounts/mailunsubscribe.html', {
        'user': user
    })

@not_logged_in
def logincode(request, code):
    logincode = LoginCode.objects.get(code=code)
    user = logincode.user
    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    if hasattr(user, 'backend'):
        auth_login(request, user)
    return profileupdate(request)

