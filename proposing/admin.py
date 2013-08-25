from models import Proposal, Comment, UpDownVote, ProposalVote, ProposalType
from django.contrib import admin
from proposing.models import Tag, Proxy, ProxyProposalVote, FinalProposalVote

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
    
    
class ProposalTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'daysUntilVotingStarts', 'minimalUpvotes', 'daysUntilVotingFinishes')

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

class ProposalAdmin(admin.ModelAdmin):
    list_display = ['title', 'voting_stage', 'discussion_time', 'creator', 'create_date', 'upvote_score', 'number_of_comments', 'views', ]
    inlines = [CommentInline, UpDownVoteInline, ProposalVoteInline]
    list_filter = ['create_date']
    actions = ['add_15_upvotes','add_15_proposalvotes','recount_votes']
    prepopulated_fields = {'slug': ('title',)}

    def add_15_upvotes(self, request, queryset):
        for proposal in queryset:
            for i in xrange(15):
                UpDownVote(user = request.user,
                post = proposal,
                value = 1).save()
                
    add_15_upvotes.short_description = "Add 15 upvotes"
    
    def add_15_proposalvotes(self, request, queryset):
        for proposal in queryset:
            for i in xrange(15):
                ProposalVote(user = request.user,
                             proposal = proposal,
                             value = 5).save()
                
    add_15_proposalvotes.short_description = "Add 15 proposal votes"

    def recount_votes(self, request, queryset):
        for proposal in queryset:
            proposal.voting_stage = 'VOTING'
            proposal.save()
                
    recount_votes.short_description = "Recount votes"


admin.site.register(Proposal, ProposalAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Proxy, ProxyAdmin)
admin.site.register(ProposalType, ProposalTypeAdmin)
admin.site.register(ProposalVote, ProposalVoteAdmin)
admin.site.register(FinalProposalVote, FinalProposalVoteAdmin)
admin.site.register(ProxyProposalVote, ProxyProposalVoteAdmin)