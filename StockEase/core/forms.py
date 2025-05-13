from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class UserForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email address',
    }))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'First name',
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Last name',
    }))
    role = forms.ChoiceField(choices=User._meta.get_field('role').choices, widget=forms.Select(attrs={
        'class': 'form-select',
    }))

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        }),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
        }),
        strip=False,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
        }

class UserUpdateForm(UserChangeForm):
    password = None  # Hide password field in update
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email address',
    }))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'First name',
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Last name',
    }))
    role = forms.ChoiceField(choices=User._meta.get_field('role').choices, widget=forms.Select(attrs={
        'class': 'form-select',
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
        }
