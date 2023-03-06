from django.contrib.auth.forms import UserCreationForm
from main.models import CustomUser
from django.forms import EmailField


# from django.contrib.auth.forms import AuthenticationForm
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email',)
        field_classes = {"email": EmailField}