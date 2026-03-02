from django.contrib.auth.models import Permission, ContentType
from api.Permission.serializer import PermissionSerializer
from rest_framework.viewsets import ModelViewSet


class PermissionViewset(ModelViewSet):
    # Identify content types for models you want to exclude
    exclude_content_types = ContentType.objects.filter(model__in=['session', 'blacklistedtoken', 'outstandingtoken', 'logentry', 'contenttype', 'permission'])
    
    # Exclude the permissions associated with those content types
    queryset = Permission.objects.exclude(content_type__in=exclude_content_types)
    serializer_class = PermissionSerializer