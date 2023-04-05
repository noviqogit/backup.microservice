from django.contrib.auth.forms import UserCreationForm
from main.models import CustomUser, Phones
from django.forms import EmailField, ModelForm, CharField, Form


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email',)
        field_classes = {"email": EmailField}


class AddPhoneNumberForm(ModelForm):
    class Meta:
        model = Phones
        fields = ('phone',)


class AddTelegramCodeForm(Form):
    code = CharField(min_length=6, max_length=32)
    password = CharField(min_length=6, max_length=32)
