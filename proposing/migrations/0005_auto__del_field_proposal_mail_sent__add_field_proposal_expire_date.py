# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Proposal.mail_sent'
        db.delete_column('proposing_proposal', 'mail_sent')

        # Adding field 'Proposal.expire_date'
        db.add_column('proposing_proposal', 'expire_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Proposal.mail_sent'
        db.add_column('proposing_proposal', 'mail_sent',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'Proposal.expire_date'
        db.delete_column('proposing_proposal', 'expire_date')


    models = {
        'accounts.customuser': {
            'Meta': {'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'avatar': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'daily_digest': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'karma': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'member_since': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 23, 0, 0)'}),
            'profile_views': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'send_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'send_favorites_and_voted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'send_finished': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'send_new': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'send_voting': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'weekly_digest': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'document.diff': {
            'Meta': {'object_name': 'Diff'},
            'fulldocument': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['document.FullDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text_representation': ('django.db.models.fields.TextField', [], {})
        },
        'document.fulldocument': {
            'Meta': {'unique_together': "(('slug', 'version'),)", 'object_name': 'FullDocument'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 23, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'proposing.comment': {
            'Meta': {'object_name': 'Comment', '_ormbases': ['proposing.VotablePost']},
            'color': ('django.db.models.fields.CharField', [], {'default': "'NEUTR'", 'max_length': '10'}),
            'motivation': ('django.db.models.fields.TextField', [], {}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['proposing.Proposal']"}),
            'votablepost_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['proposing.VotablePost']", 'unique': 'True', 'primary_key': 'True'})
        },
        'proposing.proposal': {
            'Meta': {'object_name': 'Proposal', '_ormbases': ['proposing.VotablePost']},
            'avgProposalvoteScore': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'diff': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['document.Diff']"}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'favorited_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'favorites'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'motivation': ('django.db.models.fields.TextField', [], {}),
            'proposal_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proposing.ProposalType']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'proposals'", 'symmetrical': 'False', 'to': "orm['proposing.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'votablepost_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['proposing.VotablePost']", 'unique': 'True', 'primary_key': 'True'}),
            'voting_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'voting_stage': ('django.db.models.fields.CharField', [], {'default': "'DISCUSSION'", 'max_length': '20'})
        },
        'proposing.proposaltype': {
            'Meta': {'object_name': 'ProposalType'},
            'daysUntilVotingExpires': ('django.db.models.fields.IntegerField', [], {'default': '60'}),
            'daysUntilVotingFinishes': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'daysUntilVotingStarts': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimalUpvotes': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'proposing.proposalvote': {
            'Meta': {'object_name': 'ProposalVote'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'proposal_votes'", 'to': "orm['proposing.Proposal']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'proposal_votes'", 'to': "orm['accounts.CustomUser']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'proposing.proxy': {
            'Meta': {'object_name': 'Proxy'},
            'delegates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'received_proxies'", 'symmetrical': 'False', 'to': "orm['accounts.CustomUser']"}),
            'delegating': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'proxies'", 'to': "orm['accounts.CustomUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isdefault': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'allproxies'", 'symmetrical': 'False', 'to': "orm['proposing.Tag']"})
        },
        'proposing.proxyproposalvote': {
            'Meta': {'object_name': 'ProxyProposalVote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numvotes': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'total_proxy_proposal_votes'", 'to': "orm['proposing.Proposal']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'total_proxy_proposal_votes'", 'to': "orm['accounts.CustomUser']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'vote_traject': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['accounts.CustomUser']", 'symmetrical': 'False'}),
            'voted_self': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'proposing.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'proposing.updownvote': {
            'Meta': {'object_name': 'UpDownVote'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'up_down_votes'", 'to': "orm['proposing.VotablePost']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'up_down_votes'", 'to': "orm['accounts.CustomUser']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'proposing.votablepost': {
            'Meta': {'object_name': 'VotablePost'},
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_proposals'", 'null': 'True', 'to': "orm['accounts.CustomUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'proposing.votablepostedit': {
            'Meta': {'object_name': 'VotablePostEdit'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'edits'", 'to': "orm['proposing.VotablePost']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.CustomUser']"})
        }
    }

    complete_apps = ['proposing']