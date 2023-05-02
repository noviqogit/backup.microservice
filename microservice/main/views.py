import os

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from django.core.mail import EmailMessage
from .emails.tokens import email_verification_token

from .tasks import get_history
from telegram.client import Telegram, AuthorizationState

from .forms import CustomUserCreationForm, AddPhoneNumberForm, AddTelegramCodeForm
from .models import CustomUser, Phones


class PhoneView(LoginRequiredMixin, View):
    form = AddPhoneNumberForm
    template = 'main/phone.html'
    login_url = '/login'
    redirect_field_name = 'login'

    def get(self, request):
        return render(request, self.template, context={'form': self.form()})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            Phones(phone=phone, user=request.user).save()
            return redirect('telegram', phone=phone)
        return render(request, self.template, context={'form': form})


class TelegramView(LoginRequiredMixin, View):
    form = AddTelegramCodeForm
    template = 'main/telegram.html'
    login_url = '/login'
    redirect_field_name = 'login'

    def get(self, request, phone):
        self.tg, self.state = self.telegram_request(phone)
        return render(request, self.template, context={'form': self.form()})

    def post(self, request, phone):
        form = self.form(request.POST)
        if form.is_valid():
            if self.telegram_login(code=form.cleaned_data['code'],
                                   password=form.cleaned_data['password']):
                return redirect('download')
            form.add_error('code', 'Code (or password) is not correct.')
        return render(request, self.template, context={'form': form})

    def telegram_login(self, code, password):
        if self.state == AuthorizationState.WAIT_CODE:
            self.tg.send_code(code)
            self.state = self.tg.login(blocking=False)
        if self.state == AuthorizationState.WAIT_PASSWORD:
            self.tg.send_password(password)
            self.state = self.tg.login(blocking=False)
        if self.state == AuthorizationState.READY:
            get_history.delay(self.tg)
            return True
        return False

    @staticmethod
    def telegram_request(phone):
        api_id = os.environ['api_id']
        api_hash = os.environ['api_hash']
        SECRET_KEY = os.environ['SECRET_KEY']
        tg = Telegram(
            api_id=api_id,
            api_hash=api_hash,
            phone=phone,
            database_encryption_key=SECRET_KEY,
        )
        return tg, tg.login(blocking=False)


class LoginView(View):
    form = AuthenticationForm
    template = 'main/login.html'
    success = ''

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('phone')

        return render(request, self.template, {'form': self.form})

    def post(self, request):
        form = self.form(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )

            if user is not None:
                login(request, user)
                return redirect('phone')

        return render(request, self.template, {'form': form})


class RegistrationView(View):
    form = CustomUserCreationForm
    template = 'main/registration.html'
    success = 'main/confirmation.html'

    def get(self, request):
        return render(request, self.template, context={'form': self.form()})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            user = CustomUser.objects.create_user(email=form.cleaned_data['email'],
                                                  password=form.cleaned_data["password1"])
            self.send_email_verification(user)
            return render(request, self.success, context={'email': user.email})

        return render(request, self.template, context={'form': form})

    def send_email_verification(self, user: CustomUser):
        current_site = get_current_site(self.request)
        subject = 'Activate Your Account'
        body = render_to_string(
            'main/email_verification.html', context={
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': email_verification_token.make_token(user),
            }
        )
        EmailMessage(to=[user.email], subject=subject, body=body).send()


class ConfirmationView(View):

    @staticmethod
    def get_user_from_email_verification_token(uidb64, token: str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return None

        if user and email_verification_token.check_token(user, token):
            return user

        return None

    def get(self, request, uidb64, token):
        user = self.get_user_from_email_verification_token(uidb64, token)
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('phone')
