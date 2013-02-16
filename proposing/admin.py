from models import Proposal, Comment, UpDownVote, ProposalVote
from django.contrib import admin

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
    list_display = ['creator', 'title', ]
    inlines = [CommentInline, UpDownVoteInline, ProposalVoteInline]
    list_filter = ['create_date']

admin.site.register(Proposal, ProposalAdmin)
