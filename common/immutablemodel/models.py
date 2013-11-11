# encoding: utf-8
from django.db import models

class Option(object):
    def __init__(self, name, default=None):
        self.name = name
        self.default = default
        
    def get_default_for(self, model_class):
        return self.default

class QuietOption(Option):
    def get_default_for(self, model_class):
        from django.conf import settings
        try:
            IMMUTABLE_QUIET_DEFAULT = settings.IMMUTABLE_QUIET
        except AttributeError:
            IMMUTABLE_QUIET_DEFAULT = True
        return IMMUTABLE_QUIET_DEFAULT

class FieldsOption(Option):
    def get_default_for(self, model_class):
        return []


class CantDeleteImmutableException(Exception): pass

class __Undefined(object): 
    def __len__(self):
        return False
    def __repr__(self):
        return u"__Undefined()"
UNDEFINED = __Undefined()

class PK_FIELD: pass

IMMUTABLEFIELD_OPTIONS = dict([(opt.name, opt) for opt in (
    FieldsOption('mutable_fields'),
    FieldsOption('immutable_fields'),
    QuietOption('immutable_quiet'),
    Option('immutable_lock_field', default=PK_FIELD),
    Option('immutable_is_deletable', default=True),
    )])
    

class ImmutableModelMeta(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        super_new = super(ImmutableModelMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, ImmutableModelMeta)]
        if not parents:
            # If this isn't a **sub**class of ImmutableMeta (ie. probably ImmutableModel itself), don't do anything special.
            return super_new(cls, name, bases, attrs)
        if 'Meta' in attrs:
            meta = attrs.get('Meta')
        else:
            meta = ImmutableModelMeta.meta_from_bases(bases)
        immutability_options = ImmutableModelMeta.immutable_options_from_meta(meta)
        if meta:
            stripped = ImmutableModelMeta.strip_immutability_options(meta)
        registered_model = models.base.ModelBase.__new__(cls, name, bases, attrs)
        if meta:
            ImmutableModelMeta.reattach_stripped(meta, stripped)
        ImmutableModelMeta.check_and_reinject_options(immutability_options, registered_model)
        return registered_model

    @staticmethod 
    def meta_from_bases(bases):
        for b in bases: 
            if issubclass(b, ImmutableModel) and b is not ImmutableModel:
                return getattr(b, "Meta")
                
    @staticmethod
    def immutable_options_from_meta(meta):
        immutability_options = {}
        for opt_name in IMMUTABLEFIELD_OPTIONS:
            value = getattr(meta, opt_name, UNDEFINED)
            immutability_options[opt_name] = value
        return immutability_options
    
    @staticmethod
    def strip_immutability_options(meta):
        if "immutable" in dir(meta):
            raise ValueError("immutable is not an option for ImmutableModels - use immutable_fields instead")
        stripped = {}
        for opt_name in IMMUTABLEFIELD_OPTIONS:
            if opt_name in meta.__dict__:
                stripped[opt_name] = getattr(meta, opt_name)
                delattr(meta, opt_name)
        return stripped
    
    @staticmethod
    def reattach_stripped(meta, stripped):
        for k,v in stripped.iteritems():
            setattr(meta, k, v)
             
    @staticmethod
    def check_and_reinject_options(immutability_options, model):
        for opt_name, value in immutability_options.iteritems():
            if value is UNDEFINED and getattr(model._meta, opt_name, UNDEFINED) is UNDEFINED:
                #only want to use default when registered_model doesn't have a value yet
                value = IMMUTABLEFIELD_OPTIONS[opt_name].get_default_for(model)
            if value is not UNDEFINED:
                setattr(model._meta, opt_name, value)

        if not isinstance(model._meta.immutable_fields, list):
            raise TypeError('immutable_fields attribute in %s must be '
                            'a list' % model)
        if not isinstance(model._meta.mutable_fields, list):
            raise TypeError('mutable_fields attribute in %s must be '
                            'a list' % model)
        
        if immutability_options['mutable_fields'] and immutability_options["immutable_fields"]:
            we_found = ("We found:\n" +
            ("mutable_fields: %s\n" % "mutable_fields")+
            ("immutable_fields: %s\n" % immutability_options["immutable_fields"])
            )
            raise ValueError('You can specify either mutable_fields OR immutable_fields in %s (not both).\n%s' % (model, we_found))
        
        if immutability_options["immutable_fields"]:
            model._meta.mutable_fields = [f.name for f in model._meta.fields if f.name not in immutability_options["immutable_fields"]]
        # we'll make immutable_admin_fields as the reverse of mutable fields:
        model._meta.immutable_admin_fields = [f.name for f in model._meta.fields if f.name not in model._meta.mutable_fields]
        
        if model._meta.abstract:
            # ignore immutable_lock_field in abstract models
            pass
        else:
            if model._meta.immutable_lock_field is PK_FIELD:
                model._meta.immutable_lock_field = model._meta.pk.name
            elif (isinstance(model._meta.immutable_lock_field, basestring) or 
                model._meta.immutable_lock_field is None
                ):
                pass
            else:
                raise TypeError('immutable_lock_field attribute in '
                                '%s must be a string (or None, or omitted)' % model)
        
        if not isinstance(model._meta.immutable_quiet, bool):
            raise TypeError('immutable_quiet attribute in %s must '
                            'be boolean' % model)

        if not isinstance(model._meta.immutable_is_deletable, bool):
            raise TypeError('immutable_is_deletable attribute in %s must '
                            'be boolean' % model)
            
class ImmutableModel(models.Model):
    __metaclass__ = ImmutableModelMeta
    _mutability_override = False # custom feature by Jens Nyman for getopinionated

    def can_change_field(self, field_name):
        field_changable = field_name in self._meta.mutable_fields or not self.is_immutable()
        if not field_changable and field_name == self._meta.pk.attname:
            if getattr(self, '_deleting_immutable_model', False):
                #deleting this immutable model, so need to allow Collector.delete to change the field
                return True 
        return field_changable
    
    def __setattr__(self, name, value):
        if name == '_mutability_override': # custom feature by Jens Nyman for getopinionated
            pass # setattr can continue working
        elif not self.can_change_field(name):
            # get current value
            try:
                current_value = getattr(self, name, None)
            except:
                current_value = None
            # check if this value has already been set once
            if current_value is None or current_value is '' or \
                getattr(current_value, '_file', 'not_existant') is None or \
                self.is_empty_m2m(name, current_value):
                pass
            # check if this value is actually changed
            elif current_value == value or not self.is_m2m_change(name, current_value, value):
                pass
            else:
                if self._meta.immutable_quiet:
                    return
                raise ValueError('%s.%s is immutable and cannot be changed' % (self.__class__.__name__, name))
        super(ImmutableModel, self).__setattr__(name, value)

    def is_immutable(self):
        if self._mutability_override == True: # custom feature by Jens Nyman for getopinionated
            return False
        if self.has_immutable_lock_field():
            """
            During the creation of a Django ORM object, as far as we know,
            the object starts with no fields and they are added after the object
            creation. This leads to an object with some fields created and some
            fields to create.
            In the presence of a immutable_lock field decision,
            if the field does not exists, it can be changed.
            """
            return getattr(self, self._meta.immutable_lock_field, True)
        return True

    def override_mutability(self, mutability):
        """ When override_mutability(True) is called, this object becomes a regular object (no more
        Exceptions when violating immutability).

        Note: This is a custom feature by Jens Nyman for getopinionated.

        """
        self._mutability_override = mutability

    ### m2m methods ###
    @classmethod
    def is_m2m(cls, field_name):
        """ return whether field_name is a many_to_many field.

        Note: This is used for a bugfix by Jens Nyman.

        """
        return field_name in [f.name for f in cls._meta.many_to_many]

    def is_empty_m2m(self, field_name, value):
        """ return whether this is an m2m that is empty.

        Note: This is used for a bugfix by Jens Nyman.

        """
        if self.is_m2m(field_name):
            return value.count() == 0

    def is_m2m_change(self, field_name, old_value, new_value):
        """ return whether this is an m2m that has changed from old to new.

        Note: This is used for a bugfix by Jens Nyman.

        """
        # convert old and new to comparable set
        old = set(f.pk for f in old_value.all()) # set of all id's in the RelatedManager
        new = set(int(x) for x in new_value)
        return old != new

    def has_immutable_lock_field(self):
        return self._meta.immutable_lock_field != None

    def delete(self):
        if not self._meta.immutable_is_deletable and self.is_immutable():
            if self._meta.immutable_quiet:
                return
            else:
                raise CantDeleteImmutableException(
                    "%s is immutable and cannot be deleted" % self
                )
        self._deleting_immutable_model = True
        super(ImmutableModel, self).delete()
        delattr(self, '_deleting_immutable_model')

    class Meta:
        abstract = True

