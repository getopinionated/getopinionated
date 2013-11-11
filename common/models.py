from django.db import models
from django.utils import timezone
from immutablemodel import ImmutableModel
from managers import EnabledObjectsManager

class DisableableModel(ImmutableModel):
    ### fields ###
    enabled = models.BooleanField(default=True, help_text='If False, this object is no longer active, but rather '
        'kept as reference. Unselect this instead of deleting/changing this object.')
    date_disabled = models.DateTimeField(blank=True, null=True)

    ### managers ###
    objects = models.Manager()
    enabled_objects = EnabledObjectsManager()

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
