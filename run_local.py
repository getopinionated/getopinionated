#!/usr/bin/env python
import os, shutil
from os import environ, chdir
from django.core.management import call_command

### make sure there are local settings ###
try:
    import getopinionated.local_settings
except ImportError:
    shutil.copy('getopinionated/local_settings.py.template', 'getopinionated/local_settings.py')
    print "Note: Local settings created\n"
    import getopinionated.local_settings

### validate models ###
status = os.system('python manage.py validate')
environ.setdefault("DJANGO_SETTINGS_MODULE", "getopinionated.settings")

### start server ###
if(not status):
    os.system('python manage.py syncdb --noinput')
    call_command('loaddata', 'testdata.json')
    call_command('runserver', '8000')
else:
    print "Invalid models!"
