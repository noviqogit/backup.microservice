from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField, Form, CharField, PasswordInput

from phonenumber_field.formfields import PhoneNumberField

from main.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email',)
        field_classes = {"email": EmailField}


class PhoneNumberForm(Form):
    phone = PhoneNumberField(region='RU')


class AddTelegramCodeForm(Form):
    code = CharField(min_length=5, max_length=32)
    tg_password = CharField(min_length=6, max_length=32, widget=PasswordInput)


