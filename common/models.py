from django.db import models
from immutablemodel import ImmutableModel
from managers import EnabledObjectsManager

class DisableableModel(ImmutableModel):
    ### fields ###
    enabled = models.BooleanField(default=True, help_text='If False, this object is no longer active, but rather '
        'kept as reference. Unselect this instead of deleting/changing this object.')

    ### managers ###
    objects = models.Manager()
    enabled_objects = EnabledObjectsManager()

    class Meta:
        mutable_fields = ['enabled']
        immutable_quiet = False
        immutable_is_deletable = False
        abstract = True

    def disable(self):
        self.enabled = False
        self.save()
