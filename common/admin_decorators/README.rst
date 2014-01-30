=======================
django-admin-decorators
=======================

Django's admin accepts callables for list_display and readonly_fields.
In order to customize these callables (e.g. annotate them with a description)
django requires developer to set an attribute on a callable
(e.g. 'short_description'). This is a simple approach and it works.

But it is easy to make a typo or to forget what attribute should be set
on a callable because there is no autocompletion.

This app provides an alternative (decorator) syntax for that + a couple
of other decorators useful for customizing django admin.

Installation
------------

::

    pip install django-admin-decorators

Usage
-----

::

    from django.contrib import admin
    from admin_decorators import (short_description, limit_width, boolean,
                                   apply_filter, order_field, allow_tags)
    from myapp.models import MyModel

    class MyModelAdmin(admin.ModelAdmin):
        list_display = 'name', '_text', 'has_huge_text', 'html_url'
        readonly_fields = ['name', 'html_url']

        @short_description('The text limited to 100 chars')
        @order_field('text')
        @limit_width(100)
        def _text(self, obj):
            return obj.text

        @boolean
        @short_description('The text is huge')
        def has_huge_text(self, obj):
            return len(text) > 100

        @short_description('link')
        @order_field('url')
        @allow_tags
        @apply_filter('urlize')
        def html_url(self, obj):
            return obj.url

    admin.site.register(MyModel, MyModelAdmin)

Note that ``allow_tags`` decorator marks result as safe so it will be html both
in list_display and readonly_fields.

Take a look at source code for more decorators.

Development
-----------

Development happens at
`bitbucket <https://bitbucket.org/kmike/django-admin-decorators>`_ and
`github <https://github.org/kmike/django-admin-decorators>`_.

If you've found a bug or have an idea for new decorator feel free to open
a ticket and/or send a pull request.