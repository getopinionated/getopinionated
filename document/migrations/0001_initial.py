# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FullDocument'
        db.create_table('document_fulldocument', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 6, 22, 0, 0))),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('document', ['FullDocument'])

        # Adding unique constraint on 'FullDocument', fields ['slug', 'version']
        db.create_unique('document_fulldocument', ['slug', 'version'])

        # Adding model 'Diff'
        db.create_table('document_diff', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text_representation', self.gf('django.db.models.fields.TextField')()),
            ('fulldocument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['document.FullDocument'])),
        ))
        db.send_create_signal('document', ['Diff'])


    def backwards(self, orm):
        # Removing unique constraint on 'FullDocument', fields ['slug', 'version']
        db.delete_unique('document_fulldocument', ['slug', 'version'])

        # Deleting model 'FullDocument'
        db.delete_table('document_fulldocument')

        # Deleting model 'Diff'
        db.delete_table('document_diff')


    models = {
        'document.diff': {
            'Meta': {'object_name': 'Diff'},
            'fulldocument': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['document.FullDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text_representation': ('django.db.models.fields.TextField', [], {})
        },
        'document.fulldocument': {
            'Meta': {'unique_together': "(('slug', 'version'),)", 'object_name': 'FullDocument'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 22, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['document']