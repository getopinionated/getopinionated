from django.http import HttpResponse, Http404
from django.template import Context, loader
from proposal.models import Proposal
from django.shortcuts import render, get_object_or_404


def index(request):
    first_5_proposals = Proposal.objects.order_by('create_date')[:5]
    context = {'latest_proposal_list': first_5_proposals}
    return render(request, 'proposal/index.html', context)

def detail(request, prop_id):
    prop = get_object_or_404(Proposal, pk=prop_id)
    return render(request, 'proposal/detail.html', {'proposal': prop})

def results(request, prop_id):
    return HttpResponse(
            "Hello world, you are looking at the proposal comments for proposal %s" % 
            prop_id)

def comment(request, prop_id):
    return HttpResponse(
            "Hello world, you are making a comment on proposal %s" % 
            prop_id)
