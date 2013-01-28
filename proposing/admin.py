from models import Proposal, Comment, UpDownVote
from django.contrib import admin

class CommentInline(admin.TabularInline):
    model = Comment
    fk_name = 'proposal'
    extra = 1

class VoteInline(admin.TabularInline):
    model = UpDownVote
    # fk_name = 'proposal'
    extra = 1

class ProposalAdmin(admin.ModelAdmin):
    list_display = ['creator', 'title', ]
    inlines = [CommentInline, VoteInline]
    list_filter = ['create_date']

admin.site.register(Proposal, ProposalAdmin)
