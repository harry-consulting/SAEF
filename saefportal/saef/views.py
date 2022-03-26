from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def update_notifications(request):
    """Get the unread notifications for the user and mark the notifications as read."""
    notifications = request.user.notifications.unread()
    last_five_read = request.user.notifications.read().order_by("-timestamp")[:5]

    context = {"notifications": list(notifications), "read_notifications": list(last_five_read)}

    notifications.mark_all_as_read()

    return render(request, "saef/notifications.html", context)
