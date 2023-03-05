from django.contrib.auth.forms import UserCreationForm
from main.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = 'email'

# from django.contrib.auth.forms import AuthenticationForm
