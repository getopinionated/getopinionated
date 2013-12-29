from django.db import models

class EnabledObjectsManager(models.Manager):
    """ Custom manager that uses the enabled objects as base queryset.

    For more info about custom managers, see https://docs.djangoproject.com/en/dev/topics/db/managers/.

    """
    def get_query_set(self):
        """ This method modifies the managers base queryset that contains all objects in the system.

        This method works for Django < 1.6 [TMP].

        """
        return super(EnabledObjectsManager, self).get_query_set().filter(enabled=True)

    def get_queryset(self):
        """ This method modifies the managers base queryset that contains all objects in the system.

        This method works for Django > 1.6.

        """
        return super(EnabledObjectsManager, self).get_queryset().filter(enabled=True)
