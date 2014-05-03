from os import getcwd
from os.path import exists
from shutil import copyfile
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):

    help = "Initializes the database for getopinionated for a first run"

    def handle(self, *args, **options):
        self.import_local_settings()
        self.call_command('syncdb', interactive=False)
        self.call_command('loaddata', "testdata.json")
        self.call_command('validate')   
        self.help_user_call_localserver()     

    def import_local_settings(self):

        local_settings_file = "getopinionated/local_settings.py"
        local_settings_template = "getopinionated/local_settings.py.template"

        if not exists(local_settings_file):
            print "Local settings not found, creating new %s" % local_settings_file
            print "Remember to update this file with the correct settings."
            copyfile(local_settings_template, local_settings_file)

        import getopinionated.local_settings

    def call_command(self, *args, **kwargs):
        self.stdout.write("*** Calling Command: {} ***\n".format(args[0]))
        call_command(*args, **kwargs)
        self.stdout.write("\n")

    def help_user_call_localserver(self):
        self.stdout.write("*** Done ***\n")
        self.stdout.write("If the previous succeeded, you can start your own local server using:\n\n")
        self.stdout.write("    python manage.py runserver\n\n")
