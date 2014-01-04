import datetime
import django.core.urlresolvers as urlresolvers
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.utils import timezone
from proposing.models import Tag, Proxy, ProxyProposalVote, FinalProposalVote
from models import VotablePost, Proposal, Comment, CommentReply, UpDownVote, ProposalVote, VotablePostHistory, AmendmentProposal, PositionProposal
from django.contrib.auth.models import Group
from django.utils import timezone
from common.admin import DisableableModelAdmin, DisableableTabularInline

class VotablePostAdminBase(DisableableModelAdmin):
    """ ModelAdmin for VotablePost objects """
    list_display = ['verbose_record_type']
    list_filter = DisableableModelAdmin.list_filter + ['create_date', 'is_historical_record']
    readonly_fields = DisableableModelAdmin.readonly_fields + ['is_historical_record']
    search_fields = ['creator__username']

class VotablePostTabularInlineBase(DisableableTabularInline):
    """ TabularInline for VotablePost objects """
    readonly_fields = DisableableTabularInline.readonly_fields + ['is_historical_record']

class VotablePostAdmin(VotablePostAdminBase):
    list_display = ['__unicode__', 'id', 'create_date', 'creator'] + VotablePostAdminBase.list_display

    def has_add_permission(self, request):
        return False

class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class UserInlineForProxy(admin.TabularInline):
    model = Proxy.delegates.through
    extra = 1
    
class TagInlineForProxy(admin.TabularInline):
    model = Proxy.tags.through
    extra = 1

class ProxyAdmin(DisableableModelAdmin):
    list_display = ['__unicode__', 'tags_str', 'delegating', 'isdefault', 'date_created', 'enabled']
    inlines = (TagInlineForProxy, UserInlineForProxy)
    exclude = ('tags','delegates')
    list_filter = DisableableModelAdmin.list_filter + ['date_created', 'tags']
    search_fields = ['delegating__username', 'delegates__username', 'tags__name']

class ProposalVoteAdmin(admin.ModelAdmin):
    list_display = ('user','proposal','date','value')

class FinalProposalVoteAdmin(admin.ModelAdmin):
    list_display = ('user','numvotes','voted_self','value','proposal')

class ProxyProposalVoteAdmin(admin.ModelAdmin):
    list_display = ('user_voting','user_proxied','proposal','numvotes')
    
class CommentReplyInline(VotablePostTabularInlineBase):
    model = CommentReply
    fk_name = 'comment'
    extra = 1

class CommentInline(VotablePostTabularInlineBase):
    model = Comment
    fk_name = 'proposal'
    extra = 1

class UpDownVoteInline(DisableableTabularInline):
    model = UpDownVote
    extra = 3

class ProposalVoteInline(admin.TabularInline):
    model = ProposalVote
    extra = 3

class VotablePostHistoryInline(admin.TabularInline):
    model = VotablePostHistory
    fk_name = 'post'
    extra = 0

class ProposalAdmin(VotablePostAdminBase):
    list_display = ['__unicode__', 'slug', 'voting_stage', 'creator', 'create_date', 'upvote_score', 'number_of_comments', 'number_of_edits', 'views'] + VotablePostAdminBase.list_display
    inlines = [CommentInline, UpDownVoteInline, ProposalVoteInline, VotablePostHistoryInline]
    list_filter = VotablePostAdminBase.list_filter + ['allowed_groups']
    actions = VotablePostAdminBase.actions + ['debug_updatevoting_prepare_approval','recount_votes','member_vote']
    readonly_fields = VotablePostAdminBase.readonly_fields + ['diff_link']

    def diff_link(self, obj):
        change_url = urlresolvers.reverse('admin:document:diff', args=(obj.diff.pk,))
        return '<a href="%s">%s</a>' % (str(change_url), "Go to the diff")
    
    diff_link.short_description = 'Diff-object'


    def member_vote(self, request, queryset):
        for proposal in queryset:
            proposal.allowed_groups.add(Group.objects.get(name=settings.MEMBER_GROUP_NAME))
            proposal.voting_date = timezone.now()
            proposal.voting_stage = 'VOTING'
            proposal.expire_date = timezone.now() + datetime.timedelta(days=31)
            proposal.save()
    member_vote.short_description = "Member Vote"


    def debug_updatevoting_prepare_approval(self, request, queryset):
        for proposal in queryset:
            ## create positive proposal if there are none yet
            if proposal.proposal_votes.count() == 0: 
                ProposalVote(user=request.user, proposal=proposal, value=4).save()
            ## make sure shouldBeFinished() return True
            proposal.voting_stage = 'VOTING'
            proposal.voting_date  = timezone.now() - datetime.timedelta(days=settings.VOTING_DAYS)
            proposal.save()
                
    debug_updatevoting_prepare_approval.short_description = "Debug updatevoting: prepare approval"

    def recount_votes(self, request, queryset):
        for proposal in queryset:
            proposal.voting_stage = 'VOTING'
            proposal.save()
                
    recount_votes.short_description = "Recount votes"

class CommentAdmin(VotablePostAdminBase):
    list_display = ['proposal', 'truncated_motivation', 'creator', 'create_date', 'upvote_score'] + VotablePostAdminBase.list_display + ['enabled']
    inlines = [CommentReplyInline, VotablePostHistoryInline]
    search_fields = VotablePostAdminBase.search_fields + ['proposal__title', 'motivation']

class UpDownVoteAdmin(DisableableModelAdmin):
    model = UpDownVote
    list_display = ['user', 'post', 'date', 'value', 'enabled']
    list_filter = DisableableModelAdmin.list_filter + ['date', 'value']

class VotablePostHistoryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'editing_user', 'date', 'post')
    list_filter = ['date']
    search_fields = ['editing_user__username']
    readonly_fields = ['post', 'post_at_date']

admin.site.register(VotablePost, VotablePostAdmin)
admin.site.register(AmendmentProposal, ProposalAdmin)
admin.site.register(PositionProposal, ProposalAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Proxy, ProxyAdmin)
admin.site.register(ProposalVote, ProposalVoteAdmin)
admin.site.register(FinalProposalVote, FinalProposalVoteAdmin)
admin.site.register(ProxyProposalVote, ProxyProposalVoteAdmin)
admin.site.register(UpDownVote, UpDownVoteAdmin)
admin.site.register(VotablePostHistory, VotablePostHistoryAdmin)
