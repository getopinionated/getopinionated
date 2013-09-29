GetOpinionated
==============

Little getting to-know-django-project. Together with some friends, making an online vote system, possible for use with the pirate party in Belgium.

Django specifics:
-----------------

This project is currently being developed on django. We are using the latest official release, being django 1.4.0. You can get it from https://www.djangoproject.com/download/.
You will also need scipy >0.12.0

To run the development server, run `run_local.py`. This will create the database, populate it with the data in `testdata.json` and execute `./manage.py runserver`. For a production server, make sure to add a local_settings file. For more info on this, take a look at a template file.

Dependencies:
-------------

You need a number of python modules installed on your system to be able to run getopinionated; these are:

* python-django-south
* python-django-authopenid
* python-oauth2

Furthermore, getopinionated has been developed on python 2.7.
