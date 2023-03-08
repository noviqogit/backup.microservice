from django.shortcuts import render, redirect
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model, login

from .forms import CustomUserCreationForm
from .models import CustomUser

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from django.core.mail import EmailMessage
from .emails.tokens import email_verification_token


# Create your views here.


class LoginView(View):

    def get(self, request):
        pass

    def post(self, request):
        pass


# from django.views.generic.edit import CreateView
class RegistrationView(View):
    form = CustomUserCreationForm
    template = 'main/registration.html'
    success = 'main/confirmation.html'

    def get(self, request):
        form = self.form()
        return render(request, self.template, context={'form': form})

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

    def get_user_from_email_verification_token(self, uidb64, token: str):
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
        return redirect('login')
