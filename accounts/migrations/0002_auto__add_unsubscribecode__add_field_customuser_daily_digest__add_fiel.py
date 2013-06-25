# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UnsubscribeCode'
        db.create_table('accounts_unsubscribecode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser'])),
        ))
        db.send_create_signal('accounts', ['UnsubscribeCode'])

        # Adding field 'CustomUser.daily_digest'
        db.add_column('accounts_customuser', 'daily_digest',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'CustomUser.weekly_digest'
        db.add_column('accounts_customuser', 'weekly_digest',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'CustomUser.send_new'
        db.add_column('accounts_customuser', 'send_new',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'CustomUser.send_voting'
        db.add_column('accounts_customuser', 'send_voting',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'CustomUser.send_finished'
        db.add_column('accounts_customuser', 'send_finished',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'CustomUser.send_favorites_and_voted'
        db.add_column('accounts_customuser', 'send_favorites_and_voted',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'CustomUser.send_all'
        db.add_column('accounts_customuser', 'send_all',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'UnsubscribeCode'
        db.delete_table('accounts_unsubscribecode')

        # Deleting field 'CustomUser.daily_digest'
        db.delete_column('accounts_customuser', 'daily_digest')

        # Deleting field 'CustomUser.weekly_digest'
        db.delete_column('accounts_customuser', 'weekly_digest')

        # Deleting field 'CustomUser.send_new'
        db.delete_column('accounts_customuser', 'send_new')

        # Deleting field 'CustomUser.send_voting'
        db.delete_column('accounts_customuser', 'send_voting')

        # Deleting field 'CustomUser.send_finished'
        db.delete_column('accounts_customuser', 'send_finished')

        # Deleting field 'CustomUser.send_favorites_and_voted'
        db.delete_column('accounts_customuser', 'send_favorites_and_voted')

        # Deleting field 'CustomUser.send_all'
        db.delete_column('accounts_customuser', 'send_all')


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
        'accounts.unsubscribecode': {
            'Meta': {'object_name': 'UnsubscribeCode'},
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.CustomUser']"})
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
        }
    }

    complete_apps = ['accounts']