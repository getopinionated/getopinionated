import datetime
import django.core.urlresolvers as urlresolvers
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.utils import timezone
from proposing.models import Tag, Proxy, ProxyProposalVote, FinalProposalVote
from models import Proposal, Comment, CommentReply, UpDownVote, ProposalVote, VotablePostEdit, AmendmentProposal, PositionProposal
from django.contrib.auth.models import Group
from django.utils import timezone
from common.admin import DisableableModelAdmin

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

class ProxyAdmin(admin.ModelAdmin):
    model = Proxy
    list_display = ('delegating',)
    inlines = (TagInlineForProxy,UserInlineForProxy)
    exclude = ('tags','delegates')

class ProposalVoteAdmin(admin.ModelAdmin):
    list_display = ('user','proposal','date','value')

class FinalProposalVoteAdmin(admin.ModelAdmin):
    list_display = ('user','numvotes','voted_self','value','proposal')

class ProxyProposalVoteAdmin(admin.ModelAdmin):
    list_display = ('user_voting','user_proxied','proposal','numvotes')
    
class CommentReplyInline(admin.TabularInline):
    model = CommentReply
    fk_name = 'comment'
    extra = 1

class CommentInline(admin.TabularInline):
    model = Comment
    fk_name = 'proposal'
    extra = 1

class UpDownVoteInline(admin.TabularInline):
    model = UpDownVote
    extra = 3

class ProposalVoteInline(admin.TabularInline):
    model = ProposalVote
    extra = 3

class VotablePostEditInline(admin.TabularInline):
    model = VotablePostEdit
    fk_name = 'post'
    extra = 0

class ProposalAdmin(admin.ModelAdmin):
    list_display = ['title', 'voting_stage', 'discussion_time', 'creator', 'create_date', 'upvote_score', 'number_of_comments', 'views', ]
    inlines = [CommentInline, UpDownVoteInline, ProposalVoteInline, VotablePostEditInline]
    list_filter = ['create_date', 'allowed_groups']
    actions = ['debug_updatevoting_prepare_approval','recount_votes','member_vote']
    prepopulated_fields = {'slug': ('title',)}

    readonly_fields = ['diff_link']

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

class CommentAdmin(admin.ModelAdmin):
    list_display = ['proposal', 'creator', 'create_date', 'upvote_score']
    inlines = [CommentReplyInline, VotablePostEditInline]
    list_filter = ['create_date']

class UpDownVoteAdmin(DisableableModelAdmin):
    model = UpDownVote
    list_display = ('user', 'post', 'date', 'value', 'enabled',)

admin.site.register(AmendmentProposal, ProposalAdmin)
admin.site.register(PositionProposal, ProposalAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Proxy, ProxyAdmin)
admin.site.register(ProposalVote, ProposalVoteAdmin)
admin.site.register(FinalProposalVote, FinalProposalVoteAdmin)
admin.site.register(ProxyProposalVote, ProxyProposalVoteAdmin)
admin.site.register(VotablePostEdit, admin.ModelAdmin)
admin.site.register(UpDownVote, UpDownVoteAdmin)
