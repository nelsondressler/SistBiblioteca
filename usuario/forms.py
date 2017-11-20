from django import forms
from django.utils.text import mark_safe
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm

from django.utils.translation import (
    ugettext_lazy as _,
    ugettext
)

from usuario.models import Usuario


class UserSignupForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'first_name','last_name', 'email', 'username', 'password')
        labels = {
            'first_name': _('First name'),
            'last_name': _('Last name'),
            'username': _('Usuario name')
        }
        widgets = {
            'password': forms.PasswordInput()
        }

    def save(self, commit=True):
        m = super().save(commit=False)
        m.set_password(self.cleaned_data.get('password'))

        if commit:
            m.save()

        return m

    def clean_username(self):
        username = self.cleaned_data['username']
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Usuario name already exists"))
        return username


class UserLoginForm(AuthenticationForm):
    pass


class UserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuario

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UserEditForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = (
            'first_name',
            'last_name',
            'email',
        )
