import time, json, logging, datetime

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from models import Event

@login_required
# @require_POST # CSRF is only checked on HTTP post ## TODO RE-ENABLE THIS
def ajax_notificationbarclicked(request):
    print request.user.personal_event_listeners.filter(seen_by_user=False).update(seen_by_user=True)
    return HttpResponse("ok", mimetype='text/plain')
