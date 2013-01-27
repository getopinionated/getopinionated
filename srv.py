#!/usr/bin/env python

import os
import getopinionated.local_settings

status = os.system('python manage.py validate')

if(not status):
    try:
        os.remove(DATABASE_NAME)
    except:
        pass
    os.system('python manage.py syncdb --noinput')
    os.system('python manage.py loaddata testdata.json')
    os.system('python manage.py runserver 8002')
else:
    print "Invalid models!"
