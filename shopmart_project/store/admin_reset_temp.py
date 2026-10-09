
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
    if request.method == "GET":
        return render(request, "store/admin_reset_temp.html")

    expected_token = os.environ.get("ADMIN_RESET_TOKEN", "")
    supplied_token = request.POST.get("token", "")

    if not expected_token or not hmac.compare_digest(
        supplied_token, expected_token
    ):
        return HttpResponse("Unauthorized", status=403)

    User = get_user_model()
    new_username = request.POST.get("new_username", "").strip()
    new_password = request.POST.get("new_password", "")

    if not new_username or not new_password:
        return HttpResponse(
            "Username and password are required.", status=400
        )

    admins = User.objects.filter(
        is_superuser=True,
        is_active=True,
    )

    if admins.count() == 0:
        if User.objects.filter(username=new_username).exists():
            return HttpResponse("Username already exists.", status=400)

        try:
            validate_password(new_password)
        except ValidationError as exc:
            return HttpResponse("; ".join(exc.messages), status=400)

        User.objects.create_superuser(
            username=new_username,
            email="",
            password=new_password,
        )
        return HttpResponse(
            "First admin created successfully. Log in at /admin/."
        )

    if admins.count() > 1:
        return HttpResponse(
            "Multiple active superusers exist. Automatic reset stopped; "
            "database admin identification is required.",
            status=409,
        )

    user = admins.first()

    if User.objects.filter(username=new_username).exclude(
        pk=user.pk
    ).exists():
        return HttpResponse("Username already exists.", status=400)

    try:
        validate_password(new_password, user=user)
    except ValidationError as exc:
        return HttpResponse("; ".join(exc.messages), status=400)

    user.username = new_username
    user.set_password(new_password)
    user.save()

    return HttpResponse(
        "Admin credentials updated successfully. Log in at /admin/."
    )
