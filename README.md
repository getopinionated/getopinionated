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
  * *(needed for the evaluation of the votes. An efficient inverse for sparse matrices was only added to scipy* recently)
* *[optional] python-imaging*
  * *(needed to get avatars from the users social network account)*

Furthermore, getopinionated has been developed on python 2.7.

### Installing dependencies in Ubuntu
Assuming you have python 2.7, run the following for Django:

    sudo apt-get install python-pip
    sudo pip install django==1.4

And Install the required dependencies as follows:

    sudo pip install south django-authopenid oauth2

And for scipy and python-imaging:

    sudo pip install git+http://github.com/numpy/numpy/
    sudo pip install cython
    sudo apt-get install gfortran libopenblas-dev liblapack-dev
    sudo pip install git+http://github.com/scipy/scipy/
    sudo pip install PIL

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


Github branching layout
-----------------------
http://nvie.com/posts/a-successful-git-branching-model/
