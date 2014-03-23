from django.contrib import admin
from common.admin_decorators import short_description, limit_width
from models import *

class EventAdminBase(admin.ModelAdmin):
    """ Base class for ModelAdmin for Event objects """
    list_display = ['__unicode__', 'date_created']
    list_filter = ['date_created']

class EventAdmin(EventAdminBase):
    def has_add_permission(self, request):
        return False

class PersonalEventListenerAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'seen_by_user']
    list_filter = ['seen_by_user', 'event__date_created']
    search_fields = ['user__username']
    raw_id_fields = ['event', 'user']

class PersonalEventEmailQueueAdmin(admin.ModelAdmin):
    list_display = ['event_listener']
    list_filter = ['event_listener__seen_by_user', 'event_listener__event__date_created']
    search_fields = ['event_listener__user__username']
    raw_id_fields = ['event_listener']

class GlobalEventEmailQueueAdmin(admin.ModelAdmin):
    list_display = ['event', 'already_mailed_users_str']
    list_filter = ['event__date_created']
    search_fields = ['already_mailed_users__username']
    raw_id_fields = ['event', 'already_mailed_users']

    @short_description('already mailed users')
    @limit_width(30)
    def already_mailed_users_str(self, obj):
        return ', '.join(unicode(user) for user in obj.already_mailed_users.all())

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
admin.site.register(PersonalEventListener, PersonalEventListenerAdmin)
admin.site.register(PersonalEventEmailQueue, PersonalEventEmailQueueAdmin)
admin.site.register(GlobalEventEmailQueue, GlobalEventEmailQueueAdmin)
admin.site.register(VotablePostReactionEvent, VotablePostReactionEventAdmin)
admin.site.register(ProposalLifeCycleEvent, ProposalLifeCycleEventAdmin)
admin.site.register(UpDownVoteEvent, UpDownVoteEventAdmin)
# admin.site.register(VotablePostEditEvent, VotablePostEditEventAdmin)
# admin.site.register(ProposalForkEvent, ProposalForkEventAdmin)
# admin.site.register(ProxyChangeEvent, ProxyChangeEventAdmin)
