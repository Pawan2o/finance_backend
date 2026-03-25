from django.db import models
from api.User.model import CustomUser
import json
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from threading import local
from django.conf import settings
from django.utils import timezone
import pytz
from datetime import datetime

logger = logging.getLogger(__name__)

# Constants
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')
EXCLUDED_FIELDS = {'password', 'token', 'secret', 'key'}

def convert_datetime_to_ist(value):
    """Convert datetime value to IST string format"""
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            local_time = value.astimezone(IST_TIMEZONE)
        else:
            utc_time = pytz.utc.localize(value)
            local_time = utc_time.astimezone(IST_TIMEZONE)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')
    return value

def serialize_field_value(value):
    """Serialize field value with proper datetime conversion"""
    if hasattr(value, 'pk'):
        return str(value)
    elif isinstance(value, datetime):
        return convert_datetime_to_ist(value)
    elif isinstance(value, (str, int, float, bool)) or value is None:
        return value
    else:
        return str(value)

def get_model_data(instance, sender):
    """Extract model data with proper field serialization"""
    data = {}
    for field in sender._meta.fields:
        if field.name.lower() in EXCLUDED_FIELDS:
            continue
        try:
            value = getattr(instance, field.name)
            data[field.name] = serialize_field_value(value)
        except Exception as e:
            logger.warning(f"Failed to get value for {field.name}: {e}")
    return data

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    ]
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_logs',
        db_index=True
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    module = models.CharField(max_length=100, db_index=True)  # Model name like 'Category', 'Transaction'
    object_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    changes = models.JSONField(null=True, blank=True)  # Store old and new values
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['module', 'action']),
            models.Index(fields=['timestamp', 'action']),
        ]
    
    def __str__(self):
        user_display = self.user.username if self.user else 'Anonymous'
        return f"{self.get_action_display()} on {self.module} by {user_display}"
    
    @classmethod
    def log_activity(cls, user, action, module, object_id=None, old_data=None, new_data=None, request=None):
        """Create audit log entry"""
        changes = None
        
        # Always store changes data if provided
        if old_data is not None or new_data is not None:
            changes = {}
            if old_data is not None:
                changes['old'] = old_data
            if new_data is not None:
                changes['new'] = new_data
        
        # For LOGIN/LOGOUT, store basic info
        if action in ['LOGIN', 'LOGOUT'] and not changes:
            changes = {'action': action, 'timestamp': str(timezone.now())}
        
        audit_data = {
            'user': user,
            'action': action,
            'module': module,
            'object_id': str(object_id) if object_id else None,
            'changes': changes,
        }
        
        logger.debug(f"Creating audit log: {audit_data}")
        return cls.objects.create(**audit_data)
    
# Thread-local storage for request context
_thread_locals = local()

def set_current_request(request):
    _thread_locals.request = request

def get_current_request():
    return getattr(_thread_locals, 'request', None)

def get_current_user():
    request = get_current_request()
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    return None

# Signals for auto-logging
@receiver(pre_save)
def store_original_values(sender, instance, **kwargs):
    """Store original values before update for audit tracking"""
    if sender._meta.app_label != 'api' or sender == AuditLog:
        return
    
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_values = get_model_data(original, sender)
            logger.debug(f"Stored original values for {sender.__name__} {instance.pk}")
        except sender.DoesNotExist:
            instance._original_values = {}
            logger.debug(f"No existing record found for {sender.__name__} {instance.pk}")
        except Exception as e:
            logger.error(f"Error storing original values for {sender.__name__}: {e}")
            instance._original_values = {}
    else:
        instance._original_values = {}
        logger.debug(f"New record for {sender.__name__}, no original values to store")

@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """Log model save operations"""
    try:
        if sender._meta.app_label != 'api' or sender == AuditLog:
            return
        
        user = get_current_user()
        if not user:
            logger.debug(f"No authenticated user found for {sender.__name__} operation")
            return
        
        action = 'CREATE' if created else 'UPDATE'
        new_data = get_model_data(instance, sender)
        old_data = getattr(instance, '_original_values', None) if not created else None
        
        # For UPDATE, only log if there are actual changes
        if not created and old_data is not None:
            has_changes = any(old_data.get(key) != new_value for key, new_value in new_data.items())
            if not has_changes:
                logger.debug(f"No changes detected for {sender.__name__} {instance.pk}")
                return
        
        AuditLog.log_activity(
            user=user, action=action, module=sender.__name__,
            object_id=str(instance.pk), old_data=old_data, new_data=new_data,
            request=get_current_request()
        )
        
        logger.info(f"Audit log created: {action} on {sender.__name__} by {user.username}")
        
    except Exception as e:
        logger.error(f"Error in audit logging for {sender.__name__}: {e}")

@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """Log model delete operations"""
    try:
        if sender._meta.app_label != 'api' or sender == AuditLog:
            return
            
        user = get_current_user()
        if not user:
            logger.debug(f"No authenticated user found for {sender.__name__} delete operation")
            return
        
        old_data = get_model_data(instance, sender)
        
        AuditLog.log_activity(
            user=user, action='DELETE', module=sender.__name__,
            object_id=str(instance.pk), old_data=old_data, request=get_current_request()
        )
        
        logger.info(f"Audit log created: DELETE on {sender.__name__} by {user.username}")
        
    except Exception as e:
        logger.error(f"Error in audit logging for {sender.__name__} delete: {e}")

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login events"""
    try:
        AuditLog.log_activity(user=user, action='LOGIN', module='Auth', request=request)
        logger.info(f"User login logged: {user.username}")
    except Exception as e:
        logger.error(f"Error logging user login: {e}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout events"""
    try:
        if user and user.is_authenticated:
            AuditLog.log_activity(user=user, action='LOGOUT', module='Auth', request=request)
            logger.info(f"User logout logged: {user.username}")
    except Exception as e:
        logger.error(f"Error logging user logout: {e}")