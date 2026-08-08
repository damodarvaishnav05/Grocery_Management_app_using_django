from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

from .models import CustomUser


# =========================================================
# REGISTER FORM
# =========================================================

class RegisterForm(forms.ModelForm):

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create Password",
                "id": "id_password1"
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm Password",
                "id": "id_password2"
            }
        )
    )

    class Meta:
        model = CustomUser

        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "profile_picture",
        )

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "John"
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Doe"
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "john123"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "john@gmail.com"
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+91 9876543210"
                }
            ),
        }

    def clean_username(self):

        username = self.cleaned_data["username"]

        if CustomUser.objects.filter(
            username=username
        ).exists():

            raise forms.ValidationError(
                "Username already exists."
            )

        return username

    def clean_email(self):

        email = self.cleaned_data["email"]

        if CustomUser.objects.filter(
            email=email
        ).exists():

            raise forms.ValidationError(
                "Email already exists."
            )

        return email

    def clean(self):

        cleaned = super().clean()

        if cleaned.get("password1") != cleaned.get("password2"):

            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned

    def save(self, commit=True):

        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password1"]
        )

        user.role = CustomUser.CUSTOMER

        if commit:
            user.save()

        return user


# =========================================================
# LOGIN FORM
# =========================================================

class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Username or Email"
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Password",
                "id": "id_password"
            }
        )
    )

    def clean(self):

        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:

            user = authenticate(
                username=username,
                password=password
            )

            if user is None:

                try:

                    obj = CustomUser.objects.get(
                        email=username
                    )

                    user = authenticate(
                        username=obj.username,
                        password=password
                    )

                except CustomUser.DoesNotExist:
                    pass

            if user is None:

                raise forms.ValidationError(
                    "Invalid credentials."
                )

            self.user_cache = user

        return self.cleaned_data


# =========================================================
# PROFILE FORM
# =========================================================

class ProfileForm(forms.ModelForm):

    class Meta:

        model = CustomUser

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_picture",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }

