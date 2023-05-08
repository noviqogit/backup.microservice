from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.hashers import make_password


# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, email, password):

        if email is None:
            raise TypeError('Users must have an email address.')

        if password is None:
            raise TypeError('Users must have a password.')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True, validators=[EmailValidator])

    is_active = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email

    # @property
    # def token(self):
    #     return self._generate_jwt_token()
    #
    # def _generate_jwt_token(self):
    #     dt = datetime.now() + timedelta(days=1)
    #
    #     token = jwt.encode({
    #         'id': self.pk,
    #         'exp': int(dt.strftime('%s'))
    #     }, SECRET_KEY, algorithm='HS256')
    #
    #     return jwt.decode(token, "secret", algorithms=["HS256"])


class Phones(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    phone = PhoneNumberField(null=False, blank=True, region='RU')
    code = models.CharField(null=False, blank=True, max_length=128)
    tg_password = models.CharField(null=False, blank=True, max_length=128)

    def __str__(self):
        return f'{self.user.email}, {self.phone}'


class Chats(models.Model):
    phone = models.ForeignKey(Phones, on_delete=models.CASCADE)
    chat_id = models.IntegerField()


class AgregateMessages(models.Model):
    chat_id = models.ForeignKey(Chats, on_delete=models.CASCADE)
    from_id = models.IntegerField(max_length=128)
    date = models.IntegerField(max_length=128)
    text = models.TextField(max_length=4096)
