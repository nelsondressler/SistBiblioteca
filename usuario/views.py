from django.http import Http404
from django.utils.http import is_safe_url
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from datetime import timedelta
from django.utils.timezone import now
# from allaccess.compat import get_user_model, smart_bytes, force_text
from django.utils.translation import ugettext_lazy as _

import json
from django.contrib.auth.views import (
    login as login_view,
    logout as logout_view,
    password_reset as password_reset_view,
    password_reset_done as password_reset_done_view,
    password_reset_confirm as password_reset_confirm_view,
    password_reset_complete as password_reset_complete_view
)

from usuario.models import Usuario
from usuario.utils import default_token_generator
from usuario.forms import (
    UserSignupForm,
    UserLoginForm,
    UserEditForm,
)

def user_signup(request):
    if request.method == 'POST':
        f = UserSignupForm(request.POST)
        next = request.POST.get('next')

        if f.is_valid():
            user = f.save()

            user = authenticate(email=f.cleaned_data['email'],
                password=f.cleaned_data['password'])

            user = Usuario.objects.get(username=f.cleaned_data['username'])

            if not user.check_password(f.cleaned_data['password']):
                user = None

            login(request, user)

            #user.send_verification_mail(request)

            return redirect('pesquisa')

    else:
        f = UserSignupForm()

    return render(request, 'usuario/user_signup.html', {
        'form': f
    })


def user_login(request):
    return login_view(
        request,
        authentication_form=UserLoginForm,
        template_name='usuario/user_login.html'
    )


def user_logout(request):
    return logout_view(request, next_page='home')


@login_required
def user_verification(request):
    if request.method == 'POST':
        request.user.send_verification_mail(request)

    return render(request, 'usuario/user_verification.html')


def user_verify(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = Usuario.objects.get(pk=uid)
    except (ValueError, Usuario.DoesNotExist):
        raise Http404

    if default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()

        return redirect('usuario:user_verify_done')
    else:
        raise Http404


def user_verify_done(request):
    return render(request, 'usuario/user_verify_done.html')


def user_password_reset(request):
    return password_reset_view(
        request,
        template_name='usuario/user_password_reset.html',
        email_template_name='usuario/user_password_reset_email.html',
        subject_template_name='usuario/user_password_reset_subject.txt',
        post_reset_redirect='usuario:password_reset_done'
    )


def user_password_reset_done(request):
    return password_reset_done_view(
        request,
        template_name='usuario/user_password_reset_done.html',
    )


def user_password_reset_confirm(request, uidb64, token):
    return password_reset_confirm_view(
        request,
        token=token,
        uidb64=uidb64,
        template_name='usuario/user_password_reset_confirm.html',
        post_reset_redirect='usuario:password_reset_complete'
    )


def user_password_reset_complete(request):
    return password_reset_complete_view(
        request,
        template_name='usuario/user_password_reset_complete.html'
    )


@login_required
def user_profile_edit(request):
    user = request.user
    profile = request.user.profile

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = UserProfileEditForm(request.POST, request.FILES,
                                           instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            return redirect('books:book_shelf')

    else:
        user_form = UserEditForm(instance=user)
        profile_form = UserProfileEditForm(instance=profile)

    return render(request, 'usuario/user_profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
