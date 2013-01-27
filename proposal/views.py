from django.http import HttpResponse
from django.template import Context, loader
from proposal.models import Proposal

def index(request):
    first_5_proposals = Proposal.objects.order_by('create_date')[:5]
    template = loader.get_template('proposal/index.html')
    context = Context({
        'latest_proposal_list': first_5_proposals,
    })
    return HttpResponse(template.render(context))

def detail(request, prop_id):
    return HttpResponse("Hello world, you are looking at the proposal %s" % prop_id)

def results(request, prop_id):
    return HttpResponse(
            "Hello world, you are looking at the proposal comments for proposal %s" % 
            prop_id)

def comment(request, prop_id):
    return HttpResponse(
            "Hello world, you are making a comment on proposal %s" % 
            prop_id)
