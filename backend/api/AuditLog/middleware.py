from django.utils.deprecation import MiddlewareMixin
from .model import set_current_request
import logging

logger = logging.getLogger(__name__)

class AuditLogMiddleware(MiddlewareMixin):
    """Middleware to set current request context for audit logging"""
    
    def process_request(self, request):
        """Set the current request in thread-local storage"""
        try:
            set_current_request(request)
        except Exception as e:
            logger.error(f"Error setting current request in AuditLogMiddleware: {e}")
        return None
    
    def process_response(self, request, response):
        """Clear the current request from thread-local storage"""
        try:
            set_current_request(None)
        except Exception as e:
            logger.error(f"Error clearing current request in AuditLogMiddleware: {e}")
        return response
    
    def process_exception(self, request, exception):
        """Clear the current request even if an exception occurs"""
        try:
            set_current_request(None)
        except Exception as e:
            logger.error(f"Error clearing current request after exception: {e}")
        return None