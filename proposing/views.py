from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from models import VotablePost, UpDownVote, Proposal, Comment

def index(request):
    first_5_proposals = Proposal.objects.order_by('create_date')[:5]
    context = {'latest_proposal_list': first_5_proposals}
    return render(request, 'proposal/list.html', context)

@login_required
def vote(request, post_id, updown):
    # get vars
    post = get_object_or_404(VotablePost, pk=post_id)
    proposal = post.proposal
    assert updown in ['up', 'down'], 'illegal updown value'
    # create updownvote
    vote = UpDownVote(
        user = request.user,
        post = post,
        is_up = (updown == 'up'),
    )
    vote.save()
    # redirect
    return HttpResponseRedirect(reverse('propositions-detail', args=(proposal.id,)))