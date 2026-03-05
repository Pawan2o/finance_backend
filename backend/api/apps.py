from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import api.UserProfile
        import api.Type.model
        import api.Category.model
        import api.PaymentMethod.model