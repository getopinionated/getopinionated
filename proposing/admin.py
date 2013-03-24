from models import Proposal, Comment, UpDownVote, ProposalVote, ProposalType
from django.contrib import admin
from proposing.models import Tag

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}

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
    list_display = ['title', 'voting_stage', 'proposal_type', 'creator', 'create_date', 'upvote_score', 'number_of_comments', 'views', ]
    inlines = [CommentInline, UpDownVoteInline, ProposalVoteInline]
    list_filter = ['create_date']
    actions = ['add_15_upvotes','add_15_proposalvotes']
    prepopulated_fields = {'slug': ('title',)}

    def add_15_upvotes(self, request, queryset):
        for proposal in queryset:
            for i in xrange(15):
                UpDownVote(user = request.user,
                post = proposal,
                is_up = True).save()
                
    add_15_upvotes.short_description = "Add 15 upvotes"
    
    def add_15_proposalvotes(self, request, queryset):
        for proposal in queryset:
            for i in xrange(15):
                ProposalVote(user = request.user,
                             proposal = proposal,
                             value = 5).save()
                
    add_15_proposalvotes.short_description = "Add 15 proposal votes"

admin.site.register(Proposal, ProposalAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ProposalType, ProposalTypeAdmin)
