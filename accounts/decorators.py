from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

LOGIN_REDIRECT_URL = settings.LOGIN_REDIRECT_URL

def not_logged_in(function=None, redirect_field_name=None, redirect_to=LOGIN_REDIRECT_URL):
    """
    Decorator for views that checks that the user is NOT logged in, redirecting
    to the homepage if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: not u.is_authenticated(),
        login_url=redirect_to,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def logged_in_or(additional_condition, function=None, redirect_field_name=None, redirect_to=LOGIN_REDIRECT_URL):
    """
    Decorator for views that checks that the user is NOT logged in, redirecting
    to the homepage if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() or additional_condition,
        login_url=redirect_to,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
