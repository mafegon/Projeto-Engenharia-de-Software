from django.apps import AppConfig


class PlatformApiConfig(AppConfig):
    # O schema Supabase existente usa serial/integer, não bigint.
    default_auto_field = "django.db.models.AutoField"
    name = "platform_api"
