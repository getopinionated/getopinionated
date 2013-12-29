GetOpinionated
==============

An online vote system supporting liquid democracy and document collaboration.

Dependencies:
-------------

You need a number of python modules installed on your system to be able to run getopinionated; these are:

* Django 1.4
* python-django-south
* python-django-authopenid
* python-oauth2
* *[optional] Scipy 0.12.0 or higher*
* *[optional] python-imaging*

Furthermore, getopinionated has been developed on python 2.7.

### Installing dependencies in Ubuntu
Assuming you have python 2.7, run the following for Django:

    sudo apt-get install python-pip
    sudo pip install django==1.4

And Install the other dependencies as follows:

    sudo pip install south django-authopenid oauth2

TODO: add howto install scipy (although this seems to be optional)

Getting started
---------------
To run the development server, run

    python manage.py localserver

This will create the database, populate it with the data in `testdata.json` and execute `manage.py runserver`.

Notes for setting up a production server
----------------------------------------
* Make sure to add a `local_settings.py` file. For more info on this, take a look at a template file.
* Install all optional dependencies as well
* Set up cronjob to call the following at least every 5 minutes:
    
        python manage.py updatevoting

