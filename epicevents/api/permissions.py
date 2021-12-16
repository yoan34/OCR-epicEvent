from rest_framework import permissions


class IsSeller(permissions.BasePermission):
    message = "Access denied, you're not a 'seller' user."
    def has_object_permission(self, request, view, obj):
        return True if request.user.role == 'seller' else False

class IsSupport(permissions.BasePermission):
    message = "Access denied, you're not a 'support' user."
    def has_object_permission(self, request, view, obj):
        return True if request.user.role == 'support' else False

class IsSellerResponsibleOfClient(permissions.BasePermission):
    message = "Access denied, you're not responsible of this client."
    def has_object_permission(self, request, view, obj):
        return True if request.user == obj.sale_contact else False

class IsSellerResponsibleOfContract(permissions.BasePermission):
    message = "Access denied, you're not responsible of this contract."
    def has_object_permission(self, request, view, obj):
        return True if request.user == obj.sales_contact else False

class IsSalesContact(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        print('hello')
        return True if obj.sale_contact == request.user else False


class IsObjectOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return True if obj.author == request.user else False