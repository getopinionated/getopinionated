from os import getcwd, environ, chdir
from os.path import exists, dirname
import sys
from shutil import copy, copyfile
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.management import call_command
import getopinionated.local_settings

class Command(BaseCommand):

    help = "Updates operational database"

    def handle(self, *args, **options):
        call_command('syncdb')
        call_command('migrate',auto=True,all=True)#migrate apps which already have migrations, such as social_auth

        #do the following if you created new code!    
        for app in ['proposing','document','accounts']:
            try:
                call_command('schemamigration',app,auto=True)
                pass
            except:
                print "schema migration failed for the app",app
                print "trying initial instead"
                #call_command('schemamigration',app,initial=True)
                pass
        
        print "Now automigrating all apps"
        call_command('migrate',auto=True,all=True,fake=True)
        call_command('syncdb')
        call_command('validate')
        call_command('migrate',all=True)
        
        call_command('loaddata', 'testdata.json')
        #call_command('dumpdata', 'testdata.json')
        call_command('validate')
        
        #call_command('updatevoting')
        call_command('thumbnail', 'cleanup')
        call_command('test', 'proposing')
        #call_command('collectstatic')
        
        #call_command('thumbnail', 'clear')