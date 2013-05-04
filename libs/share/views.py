from django.views.generic.edit import FormView
from share.forms import EmailForm
from django.core.mail import send_mail
from django.utils.html import escape

class EmailFormView(FormView):
  form_class = EmailForm
  template_name = 'share/email_form.html'

  def get_initial(self):
    if self.request.GET:
      data = self.request.GET.copy()
    elif self.request.POST: 
      data = self.request.GET.copy() 
    else:
      return {}

    next = data.get("next", None)

    initial = self.initial.copy()
    initial['next'] = next

    return initial
  
  def form_valid(self, form):
    send_mail('Someone wants to share something with you!', escape(form.cleaned_data['message']), escape(form.cleaned_data['email_from']), [escape(form.cleaned_data['email_to'])], fail_silently=False)
    return super(EmailFormView, self).form_valid(form)

  def get_success_url(self):
    data = self.request.POST.copy()
    next = data.get("next", None)

    if next:
      self.success_url = next

    return super(EmailFormView, self).get_success_url()