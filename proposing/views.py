from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from proposal.models import Proposal, Comment
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404


def index(request):
    first_5_proposals = Proposal.objects.order_by('create_date')[:5]
    context = {'latest_proposal_list': first_5_proposals}
    return render(request, 'proposal/index.html', context)

def vote(request, comment_id):
    c = get_object_or_404(Comment, pk=comment_id)
    p = c.proposal
    request.POST
    try:
        selected_choice = request.POST['upvote']
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'proposals/detail.html', {
            'proposal': p,
            'error_message': "Invalid upvote action.",
        })
    else:
        c.upvote += int(selected_choice) #TODO:security issue
        c.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('proposal:detail', args=(p.id,)))