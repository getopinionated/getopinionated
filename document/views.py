# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from common.shortcuts import render_to_response
from forms import ProposalForm
from django.contrib.auth.decorators import login_required
from models import FullDocument

def documentView(request, pk):
        # Initialize the form either fresh or with the appropriate POST data as the instance
    fulldocument = FullDocument.objects.get(pk=pk).getFinalVersion()
    if request.method == 'POST':
        form = ProposalForm(request.POST, instance=fulldocument)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('proposals-index'))
        else:
            pass
    else:
        form = ProposalForm(instance=fulldocument)

    return render_to_response(request, 'document/detail.html', {
        'form': form,
        'fulldocument': fulldocument
    })
