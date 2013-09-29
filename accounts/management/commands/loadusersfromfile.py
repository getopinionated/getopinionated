import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, User
from accounts.models import CustomUser

class Command(BaseCommand):
    args = '<path to the email file> [<group name>]'
    help = '''Create a new account (it the email is not yet present) for every email in the provided
              file (seperated by newlines).
              If a group name is provided, every user (with a matching email in the file) is added to
              this group.

              Arguments:
                  - path to the email file
                  - (optional) group name
           '''

    def handle(self, *args, **options):
        ## parse arguments
        try:
            # get arguments
            assert 1 <= len(args) <= 2, "One or two arguments are required for this command"
            filepath = args[0]
            groupname = args[1] if len(args) > 1 else None

            # check filepath
            assert os.path.exists(filepath), "email file not found"
            # parse file
            emails = [l.strip() for l in open(filepath).readlines()]
            # quick check on emails
            for email in emails:
                assert '@' in email, "Not every email has an @ (like {})".format(email)
                for char in "(){}[], ":
                    assert char not in email, "Illegal character ({}) en email ({})".format(char, email)
            # check for doubles
            assert len(set(emails)) == len(emails), 'There are doubles in the emails list'

            # check groupname
            if groupname:
                try:
                    group = Group.objects.get(name=groupname)
                except Group.DoesNotExist:
                    raise AssertionError('Group name does not exist')

        except AssertionError as e:
            return self.stderr.write("Error parsing arguments: {}\n\n".format(e))

        ### Part 1: create new accounts ###
        for email in emails:
            if User.objects.filter(email=email).count() == 0:
                ## generate user data
                username = email.split('@')[0]
                assert username, 'illegal email address: {}'.format(email)
                while User.objects.filter(username=username).count() != 0:
                    username += '1'
                first_name = username
                last_name = ""

                ## creat user
                self.stdout.write("Creating account for {} with username {}\n".format(email, username))
                user = CustomUser.objects.create_user(username)
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.save()
            else:
                self.stdout.write("Account already exists for {}\n".format(email))

        ### Part 2: add users to group ###
        if groupname:
            self.stdout.write("\nAdding all users in list to group '{}'...\n".format(groupname))
            for email in emails:
                user = User.objects.get(email=email)
                group.user_set.add(user)
            self.stdout.write("Done\n\n".format(groupname))

