from django.contrib import admin
from models import *

class EventAdminBase(admin.ModelAdmin):
    """ Base class for ModelAdmin for Event objects """
    list_display = ['__unicode__', 'date_created']
    list_filter = ['date_created']

class EventAdmin(EventAdminBase):
    def has_add_permission(self, request):
        return False

class VotablePostReactionEventAdmin(EventAdminBase):
    list_display = EventAdminBase.list_display + ['origin_post', 'reaction_post']

class VotablePostEditEventAdmin(EventAdminBase):
    list_display = EventAdminBase.list_display + ['edit']

class ProposalForkEventAdmin(EventAdminBase):
    list_display = EventAdminBase.list_display + ['origin_proposal', 'fork_proposal']

class UpDownVoteEventAdmin(EventAdminBase):
    list_display = EventAdminBase.list_display + ['updownvote']

class ProxyChangeEventAdmin(EventAdminBase):
    list_display = EventAdminBase.list_display + ['new_proxy', 'change_type']

class ProposalLifeCycleEventAdmin(EventAdminBase):
    list_display = EventAdminBase.list_display + ['proposal', 'new_voting_stage']

admin.site.register(Event, EventAdmin)
admin.site.register(VotablePostReactionEvent, VotablePostReactionEventAdmin)
admin.site.register(VotablePostEditEvent, VotablePostEditEventAdmin)
admin.site.register(ProposalForkEvent, ProposalForkEventAdmin)
admin.site.register(UpDownVoteEvent, UpDownVoteEventAdmin)
admin.site.register(ProxyChangeEvent, ProxyChangeEventAdmin)
admin.site.register(ProposalLifeCycleEvent, ProposalLifeCycleEventAdmin)
