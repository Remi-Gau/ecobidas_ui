from django.contrib import messages
from django.shortcuts import redirect, render

from ecobidas_ui.auth.forms import LoginForm, RegisterForm
from ecobidas_ui.views import render_error, require_methods

# TODO: implement registration and login with django.contrib.auth


@require_methods("GET", "POST")
def register(request):

    form = RegisterForm()

    if request.method == "POST":
        messages.warning(request, "REGISTER not implemented yet.")
        return render_error(request, 501)

    return render(request, "auth/register.html", {"form": form})


@require_methods("GET", "POST")
def login(request):

    form = LoginForm()

    if request.method == "POST":
        messages.warning(request, "LOGIN not implemented yet.")
        return render_error(request, 501)

    return render(request, "auth/login.html", {"form": form})


def logout(request):
    request.session.flush()
    return redirect("home")
