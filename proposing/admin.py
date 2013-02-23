from models import Proposal, Comment, UpDownVote, ProposalVote
from django.contrib import admin
from proposing.models import Tag

class ProposalInline(admin.TabularInline):
    model = Tag.proposal.through

class TagAdmin(admin.ModelAdmin):
    inlines = [
        ProposalInline,
    ]
    list_display = ('name',)
    exclude = ('proposal',)

class CommentInline(admin.TabularInline):
    model = Comment
    fk_name = 'proposal'
    extra = 1

class UpDownVoteInline(admin.TabularInline):
    model = UpDownVote
    # fk_name = 'proposal'
    extra = 3

class ProposalVoteInline(admin.TabularInline):
    model = ProposalVote
    # fk_name = 'proposal'
    extra = 3

class ProposalAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', ]
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