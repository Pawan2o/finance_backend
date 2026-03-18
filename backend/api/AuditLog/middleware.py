from django.utils.deprecation import MiddlewareMixin
from .model import set_current_request

class AuditLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        set_current_request(request)
        return None
    
    def process_response(self, request, response):
        set_current_request(None)
        return response