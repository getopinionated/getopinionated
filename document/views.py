from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from proposing.forms import AmendmentProposalForm
from proposing.models import Tag, AmendmentProposal
from models import FullDocument

def documentView(request, document_slug=settings.DEFAULT_DOCUMENT_SLUG, document_version=None):
    ## get the document
    creating_proposal = 'edit' not in request.POST
    if document_version == None:
        fulldocument = FullDocument.getFinalVersionFromSlug(document_slug)
    else:
        fulldocument = FullDocument.objects.get(slug=document_slug, version=document_version)
    form = None
    if creating_proposal:
        ## create new proposal form
        if request.user.is_authenticated() or settings.ANONYMOUS_PROPOSALS:
            if request.method == 'POST':
                assert settings.AMENDMENTS_ALLOWED
                form = AmendmentProposalForm(fulldocument, request.POST)
                if form.is_valid():
                    proposal = form.save(user=request.user)
                    messages.success(request, 'Proposal created')
                    return HttpResponseRedirect(reverse('proposals-detail', args=(proposal.slug, )))
            else:
                form = AmendmentProposalForm(fulldocument)
    else:
        ## edit proposal form
        proposal = get_object_or_404(AmendmentProposal.objects, pk=int(request.POST['edit']))
        assert proposal.isEditableBy(request.user), "You are not allowed to edit this proposal"
        assert request.method == 'POST', "the empty edit form is not created on this page"
        form = AmendmentProposalForm(fulldocument, request.POST, instance=proposal)
        if form.is_valid():
            newproposal = form.save(user=request.user)
            messages.success(request, 'Proposal edited')
            return HttpResponseRedirect(reverse('proposals-detail', args=(newproposal.slug, )))

    return render(request, 'document/detail.html', {
        'form': form,
        'fulldocument': fulldocument
    })
