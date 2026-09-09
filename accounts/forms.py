from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "phone_number",
            "password1",
            "password2",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("phone_number", "email")


class CustomSignupForm(SignupForm):

    phone_number = forms.CharField(
        max_length=11,
        label="شماره موبایل"
    )

    def save(self, request):
        user = super().save(request)

        user.phone_number = self.cleaned_data["phone_number"]

        
        user.username = self.cleaned_data["phone_number"]

        user.save()

        return user