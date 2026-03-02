from rest_framework.permissions import BasePermission, DjangoModelPermissions
from django.contrib.auth.models import Group, Permission as AuthPermission
from django.urls import resolve
import re

class CustomPermission(BasePermission):
    req = None
    allowed_groups_for_custom_api = {'admin', 'sales', 'creator', 'editor', 'manager', 'leader', 'employee', 'client', 'backoffice', 'support', 'CompanyUser'}
    
    def get_next_segment_after_api_v1(self, request):
        resolved_url = resolve(request.path_info)
        url_path = resolved_url.route
        pattern = r'^api/v1/(\w+)/'
        match = re.search(pattern, url_path)
        if match:
            extracted_word = match.group(1)
            return extracted_word
        else:
            return None  # Return None if no match is found

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        CustomPermission.req = request
        checkPermissionFor = self.get_next_segment_after_api_v1(request)
        print(f"Segment after api/v1: {checkPermissionFor}")

        if checkPermissionFor is None:
            return False

        permission_codename = self.getCode(checkPermissionFor)
        print(f"Generated permission codename: {permission_codename}")

        if not permission_codename:
            return False

        try:
            permission = AuthPermission.objects.get(codename=permission_codename)
            print(f"Found permission: {permission}")

            groups_with_permission = Group.objects.filter(permissions=permission)
            print(f"Groups with permission: {groups_with_permission}")

            user_groups = request.user.groups.all()
            print(f"User groups: {user_groups}")

            for group in user_groups:
                if group in groups_with_permission:
                    return DjangoModelPermissions().has_permission(request, view)

            return False
        except AuthPermission.DoesNotExist:
            print("Permission does not exist.")
            if request.user.is_superuser:
                return True
            if request.user and request.user.is_authenticated:
                user_groups = set(request.user.groups.values_list('name', flat=True))
                print(f"User groups: {user_groups}")
                return bool(user_groups & self.allowed_groups_for_custom_api)

    def getCode(self, codeFor):
        method = CustomPermission.req.method
        if method == 'POST':
            return 'add_' + codeFor
        elif method == 'GET':
            return 'view_' + codeFor
        elif method == 'DELETE':
            return 'delete_' + codeFor
        elif method == 'PUT' or method == 'PATCH':
            return 'change_' + codeFor
        else:
            return None  # Return None for invalid methods
        



























# class CompanyBasedPermission(BasePermission):
#     def has_permission(self, request, view):
#         # Allow all permissions for superusers
#         if request.user.is_superuser:
#             return True
#         # Use your existing custom permission logic
#         return CustomPermission().has_permission(request, view)
#     def filter_queryset(self, request, queryset, view):
#         # If the user is a superuser, return the full queryset without filtering
#         if request.user.is_superuser:
#             return queryset
#         # Otherwise, filter the queryset by the user's company
#         user_company = request.user.employee.company
#         return queryset.filter(company=user_company)


        




















# class IsCompanyUserOrReadOnly(BasePermission):
#     """
#     Allows access only to CompanyUser group for their own company's records.
#     Superusers have full access.
#     """
#     def has_permission(self, request, view):
#         if request.user.is_superuser:
#             return True
#         return request.user.groups.filter(name='CompanyUser').exists()

#     def has_object_permission(self, request, view, obj):
#         if request.user.is_superuser:
#             return True
#         return obj.company == request.user.employee.company


# class IsProjectManagerOrReadOnly(BasePermission):
#     """
#     Allows access only to ProjectManager group for their own projects.
#     Superusers have full access.
#     """
#     def has_permission(self, request, view):
#         if request.user.is_superuser:
#             return True
#         return request.user.groups.filter(name='ProjectManager').exists()

#     def has_object_permission(self, request, view, obj):
#         if request.user.is_superuser:
#             return True
#         return obj.manager == request.user.employee


# class IsTeamLeaderOrReadOnly(BasePermission):
#     """
#     Allows access only to TeamLeader group for their own team's tasks.
#     Superusers have full access.
#     """
#     def has_permission(self, request, view):
#         if request.user.is_superuser:
#             return True
#         return request.user.groups.filter(name='TeamLeader').exists()

#     def has_object_permission(self, request, view, obj):
#         if request.user.is_superuser:
#             return True
#         return obj.team.leader == request.user.employee
