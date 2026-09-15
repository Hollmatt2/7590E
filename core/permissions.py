"""Who may see and do what. The views use these checks before showing or changing anything."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Agreement, User

# Roles that work with every agreement, not only their own.
STAFF_ROLES = {User.Role.REVIEWER, User.Role.APPROVER, User.Role.ADMIN}
# Roles that identify provisions and review flags.
REVIEW_ROLES = {User.Role.REVIEWER, User.Role.APPROVER}


def can_view_agreement(user, agreement):
    """Staff roles can open any agreement. Everyone else can open only the ones they submitted."""
    return user.role in STAFF_ROLES or agreement.submitted_by_id == user.id


def can_review(user, agreement):
    """Who may decide flags and record the outcome right now.

    Reviewers and approvers review agreements that are in review; only approvers handle
    escalated ones. Nobody reviews an agreement they submitted themselves.
    """
    if agreement.submitted_by_id == user.id:
        return False
    if agreement.status == Agreement.Status.IN_REVIEW:
        return user.role in REVIEW_ROLES
    if agreement.status == Agreement.Status.ESCALATED:
        return user.role == User.Role.APPROVER
    return False


def role_required(*roles):
    """Let a view run only for logged-in users whose role is one of `roles`.

    Someone who is not logged in is sent to the login page. Someone logged in with
    another role gets a 403 "Forbidden" page.
    """
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
