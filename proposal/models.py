from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

class Proposal(models.Model):
    title = models.CharField(max_length=255)
    motivation = models.TextField()
    proposal = models.TextField()
    create_date = models.DateTimeField('Date entered')

    def __unicode__(self):
        return "%s: %s" % (self.title, self.motivation)
    
    def was_published_recently(self):
        return timezone.now() > self.create_date >= timezone.now() - datetime.timedelta(days=1)

    was_published_recently.admin_order_field = 'create_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = "Hot off the press"

class Comment(models.Model):
    proposal = models.ForeignKey(Proposal)
    comment = models.TextField()
    create_date = models.DateTimeField('Date entered')
    upvote = models.IntegerField()

    def __unicode__(self):
        return self.comment

