from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from models import VotablePost, UpDownVote, Proposal, Comment, ProposalVote
from forms import CommentForm, ProposalEditForm, CommentEditForm
from proposing.models import Tag, ProxyProposalVote
from django.db.models import Count
from proposing.forms import ProxyForm

def index(request):
    first_5_proposals = Proposal.objects.order_by('create_date')#for debugging purposes, results should actually be paginated
    taglist = Tag.objects.annotate(num_props=Count('proposals')).order_by('-num_props')
    return render(request, 'proposal/list.html', {
        'latest_proposal_list': first_5_proposals,
        'taglist': taglist
    })

def tagindex(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    proposals = tag.proposals.order_by('create_date')[:]#for debugging purposes, results should actually be paginated
    taglist = Tag.objects.annotate(num_props=Count('proposals')).order_by('-num_props')
    return render(request, 'proposal/list.html', {
        'latest_proposal_list': proposals,
        'taglist': taglist,
        'title': "Latest proposals on %s" % tag.name.lower()
    })

def detail(request, proposal_slug):
    proposal = get_object_or_404(Proposal, slug=proposal_slug)
    commentform = None
    proposal.addView()

    if proposal.commentsAllowed():
        if request.method == 'POST':
            commentform = CommentForm(request.POST)
            if commentform.is_valid():
                commentform.save(proposal, request.user)
                messages.success(request, 'Comment added')
                return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
        else:
            commentform = CommentForm()
    if proposal.voting_stage in ['APPROVED', 'REJECTED', 'EXPIRED']:
        try:
            proxyvote = ProxyProposalVote.objects.get(user=request.user,proposal=proposal)
        except ProxyProposalVote.DoesNotExist:
            proxyvote = None
    else:
        proxyvote = None
    return render(request, 'proposal/detail.html', {
        'proposal': proposal,
        'commentform': commentform,
        'proxyvote': proxyvote
    })

def editproposal(request, proposal_slug):
    proposal = get_object_or_404(Proposal, slug=proposal_slug)
    if not proposal.isEditableBy(request.user):
        return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
    if request.method == 'POST':
        editform = ProposalEditForm(request.POST, instance=proposal)
        if editform.is_valid():
            editform.save(request.user)
            messages.success(request, 'Proposal edited')
            return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
    else:
        editform = ProposalEditForm(instance=proposal)
    return render(request, 'proposal/detail.html', {
        'proposal': proposal,
        'proposaleditform': editform,
    })

def editcomment(request, proposal_slug, comment_id):
    proposal = get_object_or_404(Proposal, slug=proposal_slug)
    comment = get_object_or_404(Comment, id=comment_id)
    if not comment.isEditableBy(request.user):
        return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
    if request.method == 'POST':
        editform = CommentEditForm(request.POST, instance=comment)
        if editform.is_valid():
            editform.save(request.user)
            messages.success(request, 'Comment edited')
            return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
    else:
        editform = CommentEditForm(instance=comment)
    editform.comment_id = int(comment_id)
    return render(request, 'proposal/detail.html', {
        'commenteditform': editform,
        'proposal': proposal,
    })


@login_required
def proxy(request):
    user = request.user

    if request.method == 'POST':
        proxyform = ProxyForm(user, request.POST)
        proxyform.save()

    proxyform = ProxyForm(user)
    return render(request, 'accounts/proxy.html', {
            'user': user,
            'proxyform': proxyform,
        })


@login_required
def listofvoters(request, proposal_slug):
    proposal = get_object_or_404(Proposal, slug=proposal_slug)
    if not proposal.finishedVoting():
        raise Exception('Hacking attempt by {}'.format(request.user))
    return render(request, 'proposal/listofvoters.html', {
        'proposal': proposal,
    })

@login_required
def vote(request, proposal_slug, post_id, updown):
    # get vars
    post = get_object_or_404(VotablePost, pk=post_id)
    user = request.user
    proposal_detail_redirect = HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
    assert updown in ['up', 'down'], 'illegal updown value'
    # check if upvote can be undone
    if post.userHasUpdownvoted(user) != None:
        if post.userHasUpdownvoted(user) == updown:
            vote = post.updownvoteFromUser(user)
            vote.delete()
            messages.success(request, "Vote removed successfully")
        else:
            messages.error(request, "You already voted on this post")
        return proposal_detail_redirect
    # check if upvote is allowed
    if not post.userCanUpdownvote(user):
        messages.error(request, "You can't vote on this post")
        return proposal_detail_redirect
    # create updownvote
    vote = UpDownVote(
        user = user,
        post = post,
        value = (+1 if (updown == 'up') else -1),
    )
    vote.save()
    # redirect
    messages.success(request, "Vote successful")
    return proposal_detail_redirect

@login_required
def proposalvote(request, proposal_slug, score):
    # get vars
    proposal = get_object_or_404(Proposal, slug=proposal_slug)
    user = request.user
    proposal_detail_redirect = HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
    # check legality of vote
    assert score in dict(Proposal.voteOptions()).keys(), 'illegal vote'
    votevalue = int(float(score))
    # check if vote is in progress
    if proposal.voting_stage != 'VOTING':
        messages.error(request, "Vote is not in progress")
        return proposal_detail_redirect
    # check if user is cancelling vote
    if proposal.userHasProposalvoted(user) == votevalue:
        vote = proposal.proposalvoteFromUser(user)
        vote.delete()
        messages.success(request, "Vote removed")
        return proposal_detail_redirect
    # remove the previous vote of the user
    if proposal.userHasProposalvoted(user) != None:
        vote = proposal.proposalvoteFromUser(user)
        vote.delete()
    # create ProposalVote
    vote = ProposalVote(
        user = user,
        proposal = proposal,
        value = votevalue,
    )
    vote.save()
    # redirect
    messages.success(request, "Vote successful")
    return proposal_detail_redirect
