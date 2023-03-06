from django.shortcuts import render, HttpResponseRedirect
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .forms import CustomUserCreationForm, ConfirmationForm
from .models import CustomUser

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

    def get(self, request):
        form = self.form()
        return render(request, self.template, context={'form': form})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            form.save()
            user = CustomUser.objects.get(email=form.cleaned_data['email'])
            return HttpResponseRedirect(f'registration/{user.id}')
        return render(request, self.form, context={'form': form})

    def _send_email_verification(self, user: CustomUser):
        current_site = get_current_site(self.request)
        subject = 'Activate Your Account'
        body = render_to_string(
            'emails/email_verification.html',
            {
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': email_verification_token.make_token(user),
            }
        )
        EmailMessage(to=[user.email], subject=subject, body=body).send()


class ConfirmationView(View):
    form = ConfirmationForm
    template = 'main/registration.html'

    def get(self, request, id):
        form = self.form()
        return render(request, self.template, context={'form': form})

    def post(self, request):
        pass
