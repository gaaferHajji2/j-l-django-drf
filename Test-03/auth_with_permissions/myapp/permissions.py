from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class CanManageProducts(permissions.BasePermission):
    message = "You don't have permission to manage products."

    def has_permission(self, request, view):
        return request.user.has_perm('myapp.manage_products')

class CanViewCategories(permissions.BasePermission):
    message = "You need category viewing permission."

    def has_permission(self, request, view):
        return request.user.has_perm('myapp.view_categories')
