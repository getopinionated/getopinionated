from django.conf import settings

providers = {
  'main': ['facebook', 'twitter', 'googleplus',],
  'more': [],
}

SHARE_PROVIDERS = getattr(settings, 'SHARE_PROVIDERS', providers)