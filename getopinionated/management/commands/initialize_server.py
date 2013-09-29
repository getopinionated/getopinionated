from django.core.management.base import BaseCommand
from django.core.management import call_command
from os import getcwd
from shutil import copyfile
from os.path import exists

class Command(BaseCommand):

    help = "Initializes the database for getopinionated for a first run"

    def handle(self, *args, **options):
        self.import_local_settings()
        self.runserver()

    def import_local_settings(self):

        local_settings_file = "getopinionated/local_settings.py"
        local_settings_template = "getopinionated/local_settings.py.template"

        if not exists(local_settings_file):
            print "Local settings not found, creating new %s" % local_settings_file
            print "Remember to update this file with the correct settings."
            copyfile(local_settings_template, local_settings_file)

        import getopinionated.local_settings

    def runserver(self):
        call_command('syncdb', noinput=True)
        call_command('validate')
        call_command('runserver', '8000')

