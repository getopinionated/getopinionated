from django.conf import settings # import the settings file

def add_settings_to_context(request):
    # make all settings accessible in templates
    return {'settings': settings}
