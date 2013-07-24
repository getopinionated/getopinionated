# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VotablePost'
        db.create_table('proposing_votablepost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='created_proposals', null=True, to=orm['accounts.CustomUser'])),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('proposing', ['VotablePost'])

        # Adding model 'UpDownVote'
        db.create_table('proposing_updownvote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='up_down_votes', to=orm['accounts.CustomUser'])),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(related_name='up_down_votes', to=orm['proposing.VotablePost'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('proposing', ['UpDownVote'])

        # Adding model 'Tag'
        db.create_table('proposing_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('proposing', ['Tag'])

        # Adding model 'VotablePostEdit'
        db.create_table('proposing_votablepostedit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser'])),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(related_name='edits', to=orm['proposing.VotablePost'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('proposing', ['VotablePostEdit'])

        # Adding model 'ProposalType'
        db.create_table('proposing_proposaltype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('daysUntilVotingStarts', self.gf('django.db.models.fields.IntegerField')(default=7)),
            ('minimalUpvotes', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('daysUntilVotingFinishes', self.gf('django.db.models.fields.IntegerField')(default=7)),
            ('daysUntilVotingExpires', self.gf('django.db.models.fields.IntegerField')(default=60)),
        ))
        db.send_create_signal('proposing', ['ProposalType'])

        # Adding model 'Proposal'
        db.create_table('proposing_proposal', (
            ('votablepost_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['proposing.VotablePost'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('motivation', self.gf('django.db.models.fields.TextField')()),
            ('diff', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['document.Diff'])),
            ('views', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('voting_stage', self.gf('django.db.models.fields.CharField')(default='DISCUSSION', max_length=20)),
            ('voting_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('expire_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('discussion_time', self.gf('django.db.models.fields.IntegerField')(default=7)),
            ('avgProposalvoteScore', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('proposing', ['Proposal'])

        # Adding M2M table for field tags on 'Proposal'
        db.create_table('proposing_proposal_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proposal', models.ForeignKey(orm['proposing.proposal'], null=False)),
            ('tag', models.ForeignKey(orm['proposing.tag'], null=False))
        ))
        db.create_unique('proposing_proposal_tags', ['proposal_id', 'tag_id'])

        # Adding M2M table for field favorited_by on 'Proposal'
        db.create_table('proposing_proposal_favorited_by', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proposal', models.ForeignKey(orm['proposing.proposal'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('proposing_proposal_favorited_by', ['proposal_id', 'user_id'])

        # Adding model 'Comment'
        db.create_table('proposing_comment', (
            ('votablepost_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['proposing.VotablePost'], unique=True, primary_key=True)),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['proposing.Proposal'])),
            ('motivation', self.gf('django.db.models.fields.TextField')()),
            ('color', self.gf('django.db.models.fields.CharField')(default='NEUTR', max_length=10)),
        ))
        db.send_create_signal('proposing', ['Comment'])

        # Adding model 'ProposalVote'
        db.create_table('proposing_proposalvote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='proposal_votes', to=orm['accounts.CustomUser'])),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='proposal_votes', to=orm['proposing.Proposal'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('proposing', ['ProposalVote'])

        # Adding model 'ProxyProposalVote'
        db.create_table('proposing_proxyproposalvote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='total_proxy_proposal_votes', to=orm['accounts.CustomUser'])),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='total_proxy_proposal_votes', to=orm['proposing.Proposal'])),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('voted_self', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('numvotes', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('proposing', ['ProxyProposalVote'])

        # Adding M2M table for field vote_traject on 'ProxyProposalVote'
        db.create_table('proposing_proxyproposalvote_vote_traject', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proxyproposalvote', models.ForeignKey(orm['proposing.proxyproposalvote'], null=False)),
            ('customuser', models.ForeignKey(orm['accounts.customuser'], null=False))
        ))
        db.create_unique('proposing_proxyproposalvote_vote_traject', ['proxyproposalvote_id', 'customuser_id'])

        # Adding model 'Proxy'
        db.create_table('proposing_proxy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('delegating', self.gf('django.db.models.fields.related.ForeignKey')(related_name='proxies', to=orm['accounts.CustomUser'])),
            ('isdefault', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('proposing', ['Proxy'])

        # Adding M2M table for field delegates on 'Proxy'
        db.create_table('proposing_proxy_delegates', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proxy', models.ForeignKey(orm['proposing.proxy'], null=False)),
            ('customuser', models.ForeignKey(orm['accounts.customuser'], null=False))
        ))
        db.create_unique('proposing_proxy_delegates', ['proxy_id', 'customuser_id'])

        # Adding M2M table for field tags on 'Proxy'
        db.create_table('proposing_proxy_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proxy', models.ForeignKey(orm['proposing.proxy'], null=False)),
            ('tag', models.ForeignKey(orm['proposing.tag'], null=False))
        ))
        db.create_unique('proposing_proxy_tags', ['proxy_id', 'tag_id'])


    def backwards(self, orm):
        # Deleting model 'VotablePost'
        db.delete_table('proposing_votablepost')

        # Deleting model 'UpDownVote'
        db.delete_table('proposing_updownvote')

        # Deleting model 'Tag'
        db.delete_table('proposing_tag')

        # Deleting model 'VotablePostEdit'
        db.delete_table('proposing_votablepostedit')

        # Deleting model 'ProposalType'
        db.delete_table('proposing_proposaltype')

        # Deleting model 'Proposal'
        db.delete_table('proposing_proposal')

        # Removing M2M table for field tags on 'Proposal'
        db.delete_table('proposing_proposal_tags')

        # Removing M2M table for field favorited_by on 'Proposal'
        db.delete_table('proposing_proposal_favorited_by')

        # Deleting model 'Comment'
        db.delete_table('proposing_comment')

        # Deleting model 'ProposalVote'
        db.delete_table('proposing_proposalvote')

        # Deleting model 'ProxyProposalVote'
        db.delete_table('proposing_proxyproposalvote')

        # Removing M2M table for field vote_traject on 'ProxyProposalVote'
        db.delete_table('proposing_proxyproposalvote_vote_traject')

        # Deleting model 'Proxy'
        db.delete_table('proposing_proxy')

        # Removing M2M table for field delegates on 'Proxy'
        db.delete_table('proposing_proxy_delegates')

        # Removing M2M table for field tags on 'Proxy'
        db.delete_table('proposing_proxy_tags')


    models = {
        'accounts.customuser': {
            'Meta': {'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'avatar': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'daily_digest': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'karma': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'member_since': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 7, 23, 0, 0)'}),
            'profile_views': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'send_favorites_and_voted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'create_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 7, 23, 0, 0)'}),
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
            'discussion_time': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'favorited_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'favorites'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'motivation': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
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
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
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