from rest_framework.permissions import BasePermission, SAFE_METHODS

from hrapp.models import AbsenceRequest, Feedback


class IsManagerOrOwner(BasePermission):
    """
    Custom permission to only allow managers or owners of an object to edit it.
    Allows read-only access to co-workers (users with the same manager).
    """
    def has_object_permission(self, request, view, obj):
        # The logic for determining ownership depends on the type of object being accessed.
        # Write permissions are only granted to the manager or the owner.
        if isinstance(obj, AbsenceRequest):
            if (request.method == "PATCH" and obj.employee == request.user
                    and obj.status == AbsenceRequest.Status.PENDING
                    and request.data.get("status") == AbsenceRequest.Status.REJECTED):
                # Employees can only reject (or cancel) their absence requests when they are still pending.
                return True
            elif request.method == "PATCH" and obj.employee.profile.manager == request.user:
                # Managers can update any absence request of their employees.
                return True
            # An absence can be seen by the employee who requested it or their manager.
            return request.method == "GET" and (obj.employee == request.user or obj.employee.profile.manager == request.user)
        elif isinstance(obj, Feedback):
            # Feedback can be seen/edited by the person it's about or their manager.
            return obj.profile.user == request.user or obj.profile.manager == request.user
        # For a Profile object itself.
        return obj.user == request.user or obj.manager == request.user

class IsCoWorker(BasePermission):
    """
    Allows read-only access for co-workers.
    """
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS are GET, HEAD, OPTIONS - i.e., read-only requests.
        # Read permissions are granted for safe methods if they are co-workers.
        if request.method in SAFE_METHODS and hasattr(request.user, 'profile'):
            return obj.manager == request.user.profile.manager
        return False