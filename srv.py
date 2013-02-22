#!/usr/bin/env python
import os, shutil

### make sure there are local settings ###
try:
    import getopinionated.local_settings
except ImportError:
    shutil.copy('getopinionated/local_settings.py.template', 'getopinionated/local_settings.py')
    print "Note: Local settings created\n"
    import getopinionated.local_settings

### validate models ###
status = os.system('python manage.py validate')

### start server ###
if(not status):
    os.system('python manage.py syncdb --noinput')
    os.system('python manage.py loaddata testdata.json')
    os.system('python manage.py runserver 8000')
else:
    print "Invalid models!"
