
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
    expected_token = os.environ.get("ADMIN_RESET_TOKEN", "")
    supplied_token = request.POST.get("token", "")

    if request.method == "GET":
        return render(request, "admin_reset_temp.html")

    if not expected_token or not hmac.compare_digest(
        supplied_token, expected_token
    ):
        return HttpResponse("Unauthorized", status=403)

    User = get_user_model()
    current_username = request.POST.get("current_username", "").strip()
    new_username = request.POST.get("new_username", "").strip()
    new_password = request.POST.get("new_password", "")

    try:
        user = User.objects.get(
            username=current_username,
            is_superuser=True,
        )
    except User.DoesNotExist:
        return HttpResponse("Superuser not found.", status=404)

    if not new_username or not new_password:
        return HttpResponse("Username and password are required.", status=400)

    if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
        return HttpResponse("Username already exists.", status=400)

    try:
        validate_password(new_password, user=user)
    except ValidationError as exc:
        return HttpResponse("; ".join(exc.messages), status=400)

    user.username = new_username
    user.set_password(new_password)
    user.save()

    return HttpResponse("Admin credentials updated successfully.")
