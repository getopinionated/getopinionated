import time, json, logging, datetime
from django.utils import timezone
from django.db.models import Q, Count
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from proposing.models import Tag, ProxyProposalVote, Proxy, VotablePost, FinalProposalVote
from accounts.decorators import logged_in_or
from document.models import FullDocument
from models import VotablePost, UpDownVote, Proposal, Comment, CommentReply, ProposalVote, AmendmentProposal, PositionProposal
from forms import CommentForm, CommentReplyForm, CommentEditForm, CommentReplyEditForm, ProxyForm, AmendmentProposalForm, PositionProposalForm

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
            #might be slow
            #select edges with the correct tag
            proxies = Proxy.objects.filter(tags__pk = filter_tag.pk).filter(isdefault=False)
            #select default edges from delegating people not in the previous set
            proxies = proxies | (Proxy.objects.filter(isdefault=True).exclude(delegating__in = proxies.values('delegating')))

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

    if list_type == "following":
        if not request.user.is_authenticated():
            path = request.build_absolute_uri()
            return redirect_to_login(path)
        proposals = request.user.favorites.order_by('-create_date')
        timeline = TimelineData(
            filterkeywords = ["created", "voting_starts"],
            proposal_generators = (proposals, proposals),
            right_grey = True,
        )
    elif list_type == "latest":
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

def detail(request, proposal_slug, edit_comment_id=-1, edit_commentreply_id=-1):
    ## get vars
    proposal = get_object_or_404(Proposal, slug=proposal_slug).cast()
    commentform, commenteditform, commentreplyeditform = None, None, None
    document = None
    proposal.addView()

    ## handle all POST-requests
    if edit_comment_id != -1: ## create comment edit form
        comment_to_edit = get_object_or_404(Comment, pk=edit_comment_id)
        assert comment_to_edit.proposal.pk == proposal.pk
        if not comment_to_edit.isEditableBy(request.user):
            messages.error(request, 'This comment is not editable')
            return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
        if request.method == 'POST':
            commenteditform = CommentEditForm(request.POST, instance=comment_to_edit)
            if commenteditform.is_valid():
                commenteditform.save(request.user)
                messages.success(request, 'Comment edited')
                return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
        else:
            commenteditform = CommentEditForm(instance=comment_to_edit)

    elif edit_commentreply_id != -1: ## create commentreply edit form
        commentreply_to_edit = get_object_or_404(CommentReply, pk=edit_commentreply_id)
        assert commentreply_to_edit.comment.proposal.pk == proposal.pk
        if not commentreply_to_edit.isEditableBy(request.user):
            messages.error(request, 'This comment reply is not editable')
            return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
        if request.method == 'POST':
            commentreplyeditform = CommentReplyEditForm(request.POST, instance=commentreply_to_edit)
            if commentreplyeditform.is_valid():
                commentreplyeditform.save(request.user)
                messages.success(request, 'Comment reply edited')
                return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
        else:
            commentreplyeditform = CommentReplyEditForm(instance=commentreply_to_edit)

    elif proposal.commentsAllowedBy(request.user): ## create new comment form
        if request.method == 'POST': # POST data is for new comment form unless edit_comment_id != -1
            commentform = CommentForm(request.POST)
            if commentform.is_valid():
                commentform.save(proposal, request.user)
                messages.success(request, 'Comment added')
                return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
        else:
            commentform = CommentForm()

    ## get proxyvote (Jens: how does this work?)
    if request.user.is_authenticated() and proposal.voting_stage in ['APPROVED', 'REJECTED', 'EXPIRED']:
        try:
            proxyvote = FinalProposalVote.objects.get(user=request.user, proposal=proposal)
        except FinalProposalVote.DoesNotExist:
            proxyvote = None
    else:
        proxyvote = None

    ## get proposal edit form
    if proposal.proposaltype == 'amendment':
        proposaleditform = AmendmentProposalForm(proposal.diff.fulldocument, instance=proposal)
        proposalforkform = AmendmentProposalForm(proposal.diff.fulldocument, instance=proposal, is_edit=False)
        document = proposal.diff.fulldocument.getFinalVersion()
    else:
        proposaleditform, proposalforkform = None, None

    ## return
    return render(request, 'proposal/detail.html', {
        'proposal': proposal,
        'comments': sorted(proposal.comments.all(), key=lambda c: -c.upvote_score),
        'commentform': commentform,
        'proxyvote': proxyvote,
        'proposaleditform': proposaleditform,
        'proposalforkform': proposalforkform,
        'document': document,
        'commentreplyform': CommentReplyForm() if commentform else None,
        'commenteditform': commenteditform,
        'commentreplyeditform': commentreplyeditform,
    })

def newcommentreply(request, proposal_slug, comment_id):
    """ Note: all error checking is done by javascript. Therefore,
        all invalid input is due to hack or system error."""
    ## get vars
    proposal = get_object_or_404(Proposal, slug=proposal_slug)
    comment = get_object_or_404(Comment, id=comment_id)
    assert comment.proposal.pk == proposal.pk
    ## check if user is allowed to make new CommentReply (same policy as Comment)
    if not proposal.commentsAllowedBy(request.user):
        messages.error(request, 'Making comment replies is not allowed')
        return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))
    ## all HTTP requests should be of type post on this view
    assert request.method == 'POST'
    ## get form
    commentform = CommentReplyForm(request.POST)
    assert commentform.is_valid() # see note above
    ## get form
    commentform.save(comment, request.user)
    messages.success(request, 'Comment reply added')
    return HttpResponseRedirect(reverse('proposals-detail', args=(proposal_slug,)))

@logged_in_or(settings.ANONYMOUS_PROPOSALS)
def positionproposalform(request, edit_proposal_slug=None):
    proposalform = None
    title = None

    if edit_proposal_slug == None: # creating new proposal
        title = "New position proposal"
        if request.method == 'POST':
            proposalform = PositionProposalForm(request.POST)
            if proposalform.is_valid():
                proposal = proposalform.save(request.user)
                messages.success(request, 'Position proposal created')
                return HttpResponseRedirect(reverse('proposals-detail', args=(proposal.slug,)))
        else:
            proposalform = PositionProposalForm()
    else:
        title = "Edit proposal"
        proposal = get_object_or_404(PositionProposal, slug=edit_proposal_slug)
        if request.method == 'POST':
            proposalform = PositionProposalForm(request.POST, instance=proposal)
            if proposalform.is_valid():
                proposal = proposalform.save(request.user)
                messages.success(request, 'Proposal edited')
                return HttpResponseRedirect(reverse('proposals-detail', args=(proposal.slug,)))
        else:
            proposalform = PositionProposalForm(instance=proposal)

    ## return
    return render(request, 'proposal/positionproposal_form.html', {
        'title': title,
        'proposalform': proposalform,
    })

def proxy(request, tag_slug=None):
    tag = get_object_or_404(Tag, slug=tag_slug) if tag_slug else None
    user = request.user
    if user.is_authenticated():
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
    else:
        return render(request, 'accounts/proxy.html', {
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
@require_POST # CSRF is only checked on HTTP post
def ajaxfavorite(request, proposal_slug):
    proposal = get_object_or_404(Proposal, slug=proposal_slug)
    user = request.user
    if user in proposal.favorited_by.all():
        proposal.favorited_by.remove(user)
        proposal.save()
        return HttpResponse(content='0', mimetype='text/plain')
    else:
        proposal.favorited_by.add(user)
        proposal.save()
        return HttpResponse(content='1', mimetype='text/plain')

@login_required
@require_POST # CSRF is only checked on HTTP post
def ajaxendorse(request, proposal_slug):
    proposal = get_object_or_404(Proposal, slug=proposal_slug)
    user = request.user
    if proposal.userHasUpdownvoted(user) != None:
        vote = proposal.updownvoteFromUser(user)
        vote.delete()
        return HttpResponse(content=proposal.upvote_score, mimetype='text/plain')
    # check if upvote is allowed
    if not proposal.userCanUpdownvote(user):
        return HttpResponse(content=proposal.upvote_score, mimetype='text/plain')
    # create updownvote
    vote = UpDownVote(
        user = user,
        post = proposal,
        value = 1,
    )
    vote.save()
    return HttpResponse(content=proposal.upvote_score, mimetype='text/plain')


@login_required
@require_POST # CSRF is only checked on HTTP post
def ajaxupdownvote(request, post_id, updown):
    post = get_object_or_404(VotablePost, pk=post_id)
    user = request.user
    previous_vote = post.userHasUpdownvoted(user)
    ## user has already voted: remove it
    if previous_vote != None:
        vote = post.updownvoteFromUser(user)
        vote.delete()
    ## requested updownvote on previous_vote ==> cancels vote
    if previous_vote == updown:
        pass
    ## cast new vote
    else:
        # check if upvote is allowed
        if not post.userCanUpdownvote(user):
            return HttpResponse(content=post.upvote_score, mimetype='text/plain')
        # create updownvote
        vote = UpDownVote(
            user = user,
            post = post,
            value = (-1 if updown=="down" else 1),
        )
        vote.save()
    return HttpResponse(content=post.upvote_score, mimetype='text/plain')

@login_required
@require_POST # CSRF is only checked on HTTP post
def ajaxproposalvote(request, proposal_slug, score):
    # get vars
    proposal = get_object_or_404(Proposal, slug=proposal_slug)
    user = request.user
    ajax_response = lambda msgtype, message: HttpResponse("{}\n{}".format(msgtype, message), mimetype='text/plain')
    # check legality of vote
    assert score in dict(Proposal.voteOptions()).keys(), 'illegal vote'
    votevalue = int(float(score))
    # check if vote is in progress
    if proposal.voting_stage != 'VOTING':
        return ajax_response(msgtype='error', message="Error: vote is no longer in progress")
    # check if user is cancelling vote
    if proposal.userHasProposalvoted(user) == votevalue:
        ## cancel vote
        vote = proposal.proposalvoteFromUser(user)
        vote.delete()
        return ajax_response(msgtype='success', message="Your vote was removed")
    else:
        ## remove existing and cast new vote
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
        return ajax_response(msgtype='success', message="Your vote was cast successfully")
