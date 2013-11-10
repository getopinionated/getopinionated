=====================
django-immutablemodel
=====================
Easily make all of a django model's fields immutable after saving.
You can customize it to make some fields mutable.
You can change when it can be mutable 
(e.g. whenever the field's value is nil, or only when a particular 'lock field' is false)

History and credits
-------------------
Very heavily based on Rob Madole's original code at https://bitbucket.org/robmadole/django-immutablefield and 
Helder Silva's fork at https://bitbucket.org/skandal/django-immutablefield.
Rob's was 'inspired by a Google search that didn't turn up reusable solution for making
fields immutable inside of a Django model'.

*Pulled across from hg/bitbucket to git/github because less headache as they are more familar to me (Tim)*


Installing
----------

One of the following:

Via the ole' standby::

    easy_install django-immutablemodel

Pip::

    pip install django-immutablemodel

To install directly from Github::

    pip install git+https://github.com/red56/django-immutablemodel

.. hint:: You **do not** need to add anything into Django's ``INSTALLED_APPS``

What does it do
---------------

Allows you to declare a Django model as immutable.

It works as a drop-in replacement for Django's own ``Model``.  This means you
can ``ImmutableModel``.

::

    from django.db import models

    from immutablemodel.models import ImmutableModel

    CruiseShip(ImmutableModel):
        name = models.CharField(max_length=50)
     
        class Meta:
            mutable_fields = [] # you can actually leave this out...
			
Now you can try with all your might, but once you've saved it won't change (within reason,
sure this is Python we can do almost anything if we try hard enough)

::

    >>> queen_anne = CruiseShip.objects.create(name='Queen Anne')
    <CruiseShip 'Queen Anne'>
    >>> queen_anne.name = 'King George'
    >>> queen_anne.name
    'Queen Anne'

You can make it complain
------------------------

Change the meta section to include ``immutable_quiet = False`` and it will raise a
``ValueError`` if an attempt is made to change this value

::

    class Meta:
        mutable_fields = [] # you can actually leave this out...
        immutable_quiet = False

The error is raised as soon as you try and set the field, not when ``save()`` is
called.

::

    >>> queen_anne = CruiseShip.objects.create(name='Queen Anne')
    <CruiseShip 'Queen Anne'>
    >>> queen_anne.name = 'King George'
    ValueError: name is immutable and cannot be changed

If you want you can make ALL immutable fields complain by adding
``IMMUTABLE_QUIET=False`` to your settings.py


You can make some fields mutable
--------------------------------

List the fields you actually want mutable in "mutable_fields"

::

    CruiseShip(ImmutableModel):
        name = models.CharField(max_length=50)
		passengers = models.PositiveIntegerField()
		
        class Meta:
             mutable_fields = ['passengers'] 


Reference
---------

**Meta**

    Specify options (in addition to the normal django model's Meta options) that 
    control how immutable fields are handled when
    subclassing the ``ImmutableModel`` class

    ``mutable_fields``

        Tell ``ImmutableModel`` which fields should be allowed to change.
        This value must be a tuple or a list and contain the names of the fields
        as strings.::

            class Meta:
                mutable_fields = ['some_transient_data']

        Specify multiple fields::

            class ImmutableMeta:
                mutable_fields = ['some_transient_data', 'name', 'foreign_key']

    ``immutable_fields``

        Tell ``ImmutableModel`` which fields should not be allowed to change.
        NB: you can't specify mutable_fields AND immutable_fields.
        This value must be a tuple or a list and contain the names of the fields
        as strings.::

            class Meta:
                immutable_fields = ['my_special_id']

        Specify multiple fields::

            class ImmutableMeta:
                immutable_fields = ['my_special_id', 'name', 'foreign_key']
    
    ``immutable_quiet``

        If an attempt is made to change an immutable field, should we quietly
        prevent it.

        Set this value to ``False`` to raise a ``ValueError`` when an immutable
        field is changed.::

            class ImmutableMeta:
                immutable_quiet = False

    ``immutable_lock_field``

        This determines when to enforce immutability. By default it is equal to immutable_model.models.PK_FIELD.
        This means that when the PK_FIELD is full (typically when saved) the model is immutable, but before it is
        saved it is mutable.
        Alternatively you can specify a field by name, or you can set it to None, which means that you can't change
        immutable fields once they are set (even before saving).

            class ImmutableMeta:
                immutable_lock_field = ['is_locked']


**settings.py**

    ``IMMUTABLE_QUIET``

        Set this to ``False`` to make all immutable_fields raise an Exception when attempting
        to be changed.

