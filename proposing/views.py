import time, json, logging, datetime
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from models import VotablePost, UpDownVote, Proposal, Comment, ProposalVote
from forms import CommentForm, ProposalEditForm, CommentEditForm
from proposing.models import Tag, ProxyProposalVote, Proxy
from django.db.models import Count
from proposing.forms import ProxyForm

class TimelineData:
    # settings
    NORMAL_TIMEDELTA = 40 # days
    GREY_TIMEDELTA = 20 # days
    CAPTION_FROM_KW = {
        'created': "proposals created on ...",
        'voting_starts': "voting starts on ....",
        'voting_started': "voting started on ....",
        'voting_ends': "voting ends on ....",
        '': "",
    }
    # properties
    data = None

    def __init__(self, filterkeywords, proposal_generators, left_grey=False, right_grey=False):
        """ filterkeywords can be one of the following:
                (created, voting_starts, voting_started, voting_ends)
        """
        # TODO: truncate proposal titles

        ## get global settings
        center_day = timezone.now()
        if filterkeywords[1]:
            start_day = center_day - datetime.timedelta(days=self.GREY_TIMEDELTA if left_grey else self.NORMAL_TIMEDELTA)
            end_day = center_day + datetime.timedelta(days=self.GREY_TIMEDELTA if right_grey else self.NORMAL_TIMEDELTA)
        else:
            start_day = center_day - datetime.timedelta(days=self.NORMAL_TIMEDELTA + self.GREY_TIMEDELTA)
            end_day = center_day + datetime.timedelta(days=3)
        captions = [self.CAPTION_FROM_KW[kw] for kw in filterkeywords]
        ## preliminary data structure
        self.data = {
            'start_day': int(self.datetimeToDaystamp(start_day)),
            'center_day': self.datetimeToDaystamp(center_day),
            'end_day': int(self.datetimeToDaystamp(end_day))+1,
            'left': {
                'caption': captions[0],
                'color': '#999' if left_grey else '#000',
                'proposals': []
            },
            'right': {
                'caption': captions[1],
                'color': '#999' if right_grey else '#000',
                'proposals': []
            },
        }
        ## fill in proposals
        for leftright, proposals, filterkeyword, daterange in zip(['left', 'right'], \
                proposal_generators, filterkeywords, \
                [(start_day, center_day), (center_day, end_day)]):
            if filterkeyword == 'created':
                proposals = proposals.filter(create_date__range=daterange)
                proposals = [(prop.create_date, prop) for prop in proposals]
            elif filterkeyword == 'voting_starts':
                proposals = proposals.filter(voting_date__range=daterange)
                proposals = [(prop.voting_date, prop) for prop in proposals]
            elif filterkeyword == 'voting_started':
                proposals = proposals.filter(voting_date__range=daterange)
                proposals = [(prop.voting_date, prop) for prop in proposals]
            elif filterkeyword == 'voting_ends':
                proposals = proposals.filter(voting_stage='VOTING')
                proposals = [(prop.estimatedFinishDate, prop) for prop in proposals]
                proposals = [(date, prop) for (date, prop) in proposals if daterange[0] <= date <= daterange[1]]
            elif filterkeyword == '':
                continue
            proposals = sorted(proposals)
            for date, prop in proposals:
                self.data[leftright]['proposals'].append([
                    prop.title,
                    reverse('proposals-detail', args=(prop.slug,)),
                    self.datetimeToDaystamp(date),
                    '{d.day} {d:%b}'.format(d=date), # e.g.: "24 May"
                ])

    def toJson(self):
        return json.dumps(self.data)

    @staticmethod
    def datetimeToDaystamp(d):
        SECONDS_IN_DAY = 24*60*60
        return time.mktime(d.timetuple()) / SECONDS_IN_DAY

class ProxyGraphData:
    # properties
    dataNodes = None
    dataEdges = None

    def __init__(self, filter_tag=None):
        nodes = set()
        ## fill in edges
        self.dataEdges = []
        if not filter_tag:
            proxies = Proxy.objects.all()
        else:
            proxies = Proxy.objects.filter(Q(tags__in=[filter_tag.id]) | Q(tags=None))
        for proxy in proxies:
            nodes.add(proxy.delegating.display_name)
            for delegate in proxy.delegates.all():
                nodes.add(delegate.display_name)
                self.dataEdges.append(r"['{}', '{}', {{color: '{}'}}]".format(
                    proxy.delegating.display_name,
                    delegate.display_name,
                    '#0C3' if proxy.tags.count() else '#000',
                ))

        ## fill in nodes
        self.dataNodes = list(nodes)

    def nodesToJson(self):
        return json.dumps({'nodes': self.dataNodes})

    def edgesToArgs(self):
        return ','.join(self.dataEdges)


def proplist(request, list_type="latest"):
    # TODO: pagination

    if list_type == "latest":
        proposals = Proposal.objects.order_by('-create_date')
        timeline = TimelineData(
            filterkeywords = ["created", "voting_starts"],
            proposal_generators = (proposals, proposals),
            right_grey = True,
        )
    elif list_type == "voting":
        proposals = Proposal.objects.filter(voting_stage='VOTING').order_by('-voting_date')
        timeline = TimelineData(
            filterkeywords = ["voting_started", "voting_ends"],
            proposal_generators = (proposals, proposals),
            left_grey = True,
        )
    elif list_type == "all":
        proposals = Proposal.objects.order_by('-create_date')
        timeline = TimelineData(
            filterkeywords = ["created", ""],
            proposal_generators = (proposals, proposals),
            right_grey = True,
        )
    taglist = Tag.objects.annotate(num_props=Count('proposals')).order_by('-num_props')
    return render(request, 'proposal/list.html', {
        'latest_proposal_list': proposals,
        'taglist': taglist,
        'timeline': timeline,
    })

def tagproplist(request, tag_slug):
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
    if request.user.is_authenticated() and proposal.voting_stage in ['APPROVED', 'REJECTED', 'EXPIRED']:
        try:
            proxyvote = ProxyProposalVote.objects.get(user=request.user, proposal=proposal)
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
def proxy(request, tag_slug=None):
    tag = get_object_or_404(Tag, slug=tag_slug) if tag_slug else None
    user = request.user

    if request.method == 'POST':
        proxyform = ProxyForm(user, request.POST)
        proxyform.save()

    proxyform = ProxyForm(user)
    return render(request, 'accounts/proxy.html', {
            'user': user,
            'proxyform': proxyform,
            'proxygraph': ProxyGraphData(tag),
            'tags': Tag.objects.all(),
            'filter_tag': tag,
        })


@login_required
def listofvoters(request, proposal_slug):
    proposal = get_object_or_404(Proposal, slug=proposal_slug)
    if not proposal.finishedVoting:
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
