
import hmac
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def temporary_admin_reset(request):
    # Reset token must be configured in Render Environment
    expected_token = os.environ.get("ADMIN_RESET_TOKEN", "")

    if request.method == "GET":
        return render(request, "store/admin_reset_temp.html")

    supplied_token = request.POST.get("token", "")

    # Verify secret token
    if not expected_token or not hmac.compare_digest(
        supplied_token, expected_token
    ):
        return HttpResponse("Unauthorized", status=403)

    User = get_user_model()

    current_username = request.POST.get(
        "current_username", ""
    ).strip()
    new_username = request.POST.get("new_username", "").strip()
    new_password = request.POST.get("new_password", "")

    if not current_username or not new_username or not new_password:
        return HttpResponse(
            "All fields are required.", status=400
        )

    # Find the existing active superuser
    try:
        user = User.objects.get(
            username=current_username,
            is_superuser=True,
            is_active=True,
        )
    except User.DoesNotExist:
        return HttpResponse(
            "Active superuser not found.", status=404
        )

    # Prevent duplicate usernames
    if User.objects.filter(username=new_username).exclude(
        pk=user.pk
    ).exists():
        return HttpResponse(
            "Username already exists.", status=400
        )

    # Validate new password
    try:
        validate_password(new_password, user=user)
    except ValidationError as exc:
        return HttpResponse(
            " ".join(exc.messages), status=400
        )

    # Update credentials
    user.username = new_username
    user.set_password(new_password)
    user.save()

    return HttpResponse(
        "Admin credentials updated successfully. "
        "You can now log in at /admin/."
    )
