from django.conf import settings

providers = {
  'main': ['facebook', 'twitter', 'pinterest', 'googleplus',],
  'more': ['email', 'print',],
}

SHARE_PROVIDERS = getattr(settings, 'SHARE_PROVIDERS', providers)