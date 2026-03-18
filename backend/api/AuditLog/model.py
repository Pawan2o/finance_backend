from django.db import models
from api.User.model import CustomUser
import json
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from threading import local

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
    user_agent = models.TextField(null=True, blank=True)
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
        if old_data is not None or new_data is not None:
            changes = {}
            if old_data is not None:
                changes['old'] = old_data
            if new_data is not None:
                changes['new'] = new_data
        
        audit_data = {
            'user': user,
            'action': action,
            'module': module,
            'object_id': str(object_id) if object_id else None,
            'changes': changes,
        }
        
        if request:
            audit_data.update({
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            })
        
        return cls.objects.create(**audit_data)
    
    @classmethod
    def debug_ip_headers(cls, request):
        """Debug method to see all IP-related headers"""
        # This method is no longer needed since IP tracking is removed
        return {"message": "IP tracking has been disabled"}
    


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
    if sender._meta.app_label != 'api' or sender == AuditLog:
        return
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_values = {}
            for field in sender._meta.fields[:5]:
                try:
                    value = getattr(original, field.name)
                    if hasattr(value, 'pk'):
                        instance._original_values[field.name] = str(value)
                    elif hasattr(value, '__str__'):
                        instance._original_values[field.name] = str(value)
                    else:
                        instance._original_values[field.name] = value
                except:
                    pass
        except sender.DoesNotExist:
            instance._original_values = {}
    else:
        instance._original_values = {}

@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    try:
        if sender._meta.app_label != 'api' or sender == AuditLog:
            return
        
        # Debug print
        print(f"Signal triggered for {sender.__name__}: {instance.pk}")
        
        user = get_current_user()
        if not user:
            print("No current user found")
            return
        
        print(f"Current user: {user.username}")
        
        action = 'CREATE' if created else 'UPDATE'
        new_data = {}
        for field in sender._meta.fields[:5]:
            try:
                value = getattr(instance, field.name)
                if hasattr(value, 'pk'):
                    new_data[field.name] = str(value)
                elif hasattr(value, '__str__'):
                    new_data[field.name] = str(value)
                else:
                    new_data[field.name] = value
            except:
                pass
        
        old_data = getattr(instance, '_original_values', None) if not created else None
        
        audit_log = AuditLog.log_activity(
            user=user, action=action, module=sender.__name__,
            object_id=str(instance.pk), old_data=old_data, new_data=new_data,
            request=get_current_request()
        )
        print(f"Created audit log: {audit_log.id}")
        
    except Exception as e:
        print(f"Error in audit logging: {e}")
        # Silent fail to prevent breaking the main operation
        pass

@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    try:
        if sender._meta.app_label != 'api' or sender == AuditLog:
            return
        user = get_current_user()
        if not user:
            return
        
        old_data = {}
        for field in sender._meta.fields[:5]:
            try:
                value = getattr(instance, field.name)
                if hasattr(value, 'pk'):
                    old_data[field.name] = str(value)
                elif hasattr(value, '__str__'):
                    old_data[field.name] = str(value)
                else:
                    old_data[field.name] = value
            except:
                pass
        
        AuditLog.log_activity(
            user=user, action='DELETE', module=sender.__name__,
            object_id=str(instance.pk), old_data=old_data, request=get_current_request()
        )
    except Exception as e:
        # Silent fail to prevent breaking the main operation
        pass

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    try:
        AuditLog.log_activity(user=user, action='LOGIN', module='Auth', request=request)
    except:
        pass

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    try:
        if user and user.is_authenticated:
            AuditLog.log_activity(user=user, action='LOGOUT', module='Auth', request=request)
    except:
        pass