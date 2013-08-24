GetOpinionated
==============

Little getting to-know-django-project. Together with some friends, making an online vote system, possible for use with the pirate party in Belgium.

Django specifics:
-----------------

This project is currently being developed on django. We are using the latest official release, being django 1.4.3. You can get it from https://www.djangoproject.com/download/.

To run the development server, run `srv.py`. This will create the database, populate it with the data in `testdata.json` and execute `./manage.py runserver`.

Dependencies:
-------------

You need a number of python modules installed on your system to be able to run getopinionated; these are:

* python-django-south
* python-django-authopenid
* python-oauth2

Furthermore, getopinionated has been developed on python 2.7.
