from rest_framework import status
from rest_framework.views import exception_handler


def permission_denied_exception_handler(exc, context):
    """If the object exist but the user does not have permission for it, change the status code and message."""
    # Call REST framework's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    if context["view"].queryset:
        model = context["view"].queryset.model

        if (response.status_code == status.HTTP_404_NOT_FOUND and
                model.objects.filter(id=context["kwargs"]["pk"]).exists()):
            response.status_code = status.HTTP_403_FORBIDDEN
            response.data["detail"] = "You do not have permission to perform this action."

    return response
