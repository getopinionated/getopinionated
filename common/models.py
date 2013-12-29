from django.db import models
from django.utils import timezone
from immutablemodel import ImmutableModel
from managers import EnabledObjectsManager
from copy import copy

class DisableableModel(ImmutableModel):
    ### fields ###
    enabled = models.BooleanField(default=True, help_text='If False, this object is no longer active, but rather '
        'kept as reference. Unselect this instead of deleting/changing this object.')
    date_disabled = models.DateTimeField(blank=True, null=True)

    ### managers ###
    all_objects = models.Manager()
    objects = EnabledObjectsManager()

    class Meta:
        mutable_fields = []
        immutable_quiet = False
        immutable_is_deletable = False
        abstract = True

    def disable(self):
        """ Disable this object.

        Note: This is the only way in which the enable flag can change.

        """
        self.override_mutability(True)
        self.enabled = False
        self.date_disabled = timezone.now()
        self.save()
        self.override_mutability(False)

    def disable_and_get_mutable_copy(self, save=True):
        """ disable this object and make a copy """
        # make copy
        copy_obj = self.get_mutable_copy(save)

        # disable
        self.disable()

        return copy_obj

    def get_mutable_copy(self, save=True):
        # make copy
        def copy_this_field(fieldname):
            if fieldname in ['pk', 'id', 'slug']: # filter normally unique fields
                return False
            if fieldname.endswith('_ptr'): # fix inheritance bug on clone
                return False
            return True

        new_kwargs = dict([(fld.name, getattr(self, fld.name)) for fld in self._meta.fields if copy_this_field(fld.name)]);
        copy_obj = self.__class__(**new_kwargs)

        # will be copied on save (see https://docs.djangoproject.com/en/1.4/topics/db/queries/#copying-model-instances)
        if save:
            copy_obj.save()
        return copy_obj

    ## OLD IMPLEMENTATION ##
    # def get_mutable_copy(self, save=True):
    #     # make raw copy
    #     copy_obj = copy(self)

    #     # will be copied on save (see https://docs.djangoproject.com/en/1.4/topics/db/queries/#copying-model-instances)
    #     copy_obj.override_mutability(True)
    #     copy_obj.pk = None
    #     copy_obj.id = None
    #     if save:
    #         copy_obj.save()
    #     return copy_obj


