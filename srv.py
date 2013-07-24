#!/usr/bin/env python

from os import environ, chdir
from os.path import exists, dirname
from shutil import copy
from django.core.management import call_command

def chdir_to_project():
    if dirname(__file__):
        chdir(dirname(__file__))

def import_local_settings():
    local_settings_file = "getopinionated/local_settings.py"
    local_settings_template = "getopinionated/local_settings.py.template"
    if not exists(local_settings_file):
        print "Local settings not found, creating new %s" % local_settings_file
        #This doesn't work on my Linux, Jonas
        #copy(local_settings_file, local_settings_template)
    import getopinionated.local_settings

def runserver():
    chdir_to_project()
    import_local_settings()
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
    #call_command('runserver', '8000')

if __name__ == "__main__":
    environ.setdefault("DJANGO_SETTINGS_MODULE", "getopinionated.settings")
    runserver()
