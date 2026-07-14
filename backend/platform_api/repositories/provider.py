from django.conf import settings


def get_repository():
    if settings.PLATFORM_REPOSITORY == "django":
        from platform_api.repositories.django import repository
    else:
        from platform_api.repositories.memory import repository
    return repository


repository = get_repository()
