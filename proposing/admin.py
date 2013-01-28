from models import Proposal, Comment
from django.contrib import admin

class CommentInline(admin.TabularInline):
    model = Comment
    fk_name = 'proposal'
    extra = 1

class ProposalAdmin(admin.ModelAdmin):
    list_display = ['creator', 'title', ]
    inlines = [CommentInline]
    list_filter = ['create_date']

admin.site.register(Proposal, ProposalAdmin)
