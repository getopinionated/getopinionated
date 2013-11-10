# encoding: utf-8
from django.contrib import admin

class ImmutableModelAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        # Override super class method, in order to achieve readonly fields, at
        # signed-off entities forms
        def reload_obj():
            return obj.__class__.objects.get(pk=obj.pk)

        if not obj is None:
            # We'r chaging the obj
            immutable_lock_field_name = obj._meta.immutable_lock_field
            if not getattr(reload_obj(), immutable_lock_field_name, False):
                return self.readonly_fields + tuple([immutable_lock_field_name])
            return self.readonly_fields + tuple(obj._meta.immutable_admin_fields)
        else:
            return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        if not obj.immutable_is_deletable and obj.is_immutable():
            return False
        return super(ImmutableModelAdmin, self).has_delete_permission(
            request,
            obj,
        )

class ComplexImmutableModelAdmin(ImmutableModelAdmin):
    save_as = True
    fields = ('immutable_lock',)

    def _validate_and_check_immutable_immutable_lock_request(self, request, obj):
        if 'immutable_lock' in request.POST and request.POST['immutable_lock'] == 'on':
            try:
                setattr(obj, obj._meta.immutable_lock_field, True)
            except AttributeError:
                pass

            obj.save()

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not obj is None and obj.is_immutable():
            context['adminform'].form.fields['immutable_lock'].widget.attrs['disabled'] = True

        return super(ComplexImmutableModelAdmin, self).render_change_form(
            request,
            context,
            add,
            change,
            form_url,
            obj,
        )

    def change_view(self, request, object_id, extra_context=None):
        if extra_context is None:
            extra_context = {}

        obj = self.get_object(request, int(object_id))

        # Overriding the "_saveasnew" particular case, for readonly fields
        # treatment purposes
        if '_saveasnew' in request.POST:
            request.method = 'GET'
            try:
                immutable_lock_field_name = obj._meta.immutable_lock_field
            except AttributeError:
                immutable_lock_field_name = ""

            fields_dict = {}
            fields_dict.update(
                dict([
                    (field.name, field._get_val_from_obj(obj))
                    for field in obj._meta.fields
                    if field.name != immutable_lock_field_name
                ])
            )

            fields_dict.update(
                dict((
                    field.name,
                    ",".join([
                        str(s.pk) for s in
                        getattr(obj, field.name).all()
                    ]),)
                    for field in (_f for _f in obj._meta.many_to_many)
                    if field.name != immutable_lock_field_name
                )
            )

            request_get_copy = request.GET.copy()
            request_get_copy.update(fields_dict)
            request.GET = request_get_copy

            return self.add_view(request, form_url='../add/')

        return super(ComplexImmutableModelAdmin, self).change_view(
            request,
            object_id,
            extra_context,
        )


    def response_change(self, request, obj):
        response = super(ComplexImmutableModelAdmin, self).response_change(request,obj)
        self._validate_and_check_immutable_immutable_lock_request(request, obj)

        return response

    def response_add(self, request, obj):
        response = super(ComplexImmutableModelAdmin, self).response_add(request,obj)
        self._validate_and_check_immutable_immutable_lock_request(request, obj)

        return response
