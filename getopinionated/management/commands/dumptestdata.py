from os import getcwd
from os.path import exists
import sys
from shutil import copyfile
from django.core.management.base import BaseCommand
from django.core.management import call_command

_FILENAME = 'testdata.json'

class Command(BaseCommand):

    help = "Creates a json dumpdata files called 'testdata.json'"

    def handle(self, *args, **options):
        # equivalent of:
        #   python manage.py dumpdata -e contenttypes -e sessions -e admin -e auth.permission --indent=4 > testdata.json
        args = ['dumpdata']
        kwargs = {'indent': 4, 'exclude': ['contenttypes', 'sessions', 'admin', 'auth.permission']}

        # redirect sysout to a file (see http://stackoverflow.com/questions/16075789/how-to-use-call-command-with-dumpdata-command-to-save-json-to-file)
        sysout = sys.stdout
        sys.stdout = open(_FILENAME, 'w')
        call_command(*args, **kwargs)
        sys.stdout = sysout

        # clean up right space in testdata.json
        lines = open(_FILENAME).readlines()
        lines = [l.rstrip() for l in lines]

        # remove frequently changing fields
        lines = [l for l in lines if '"last_login": "' not in l]
        
        filtered_content = '\n'.join(lines)
        open(_FILENAME, 'w').write(filtered_content)


