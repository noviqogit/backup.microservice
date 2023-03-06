from django.shortcuts import render, HttpResponseRedirect
from django.views import View
from .forms import CustomUserCreationForm, ConfirmationForm
from .models import CustomUser


# Create your views here.


class LoginView(View):

    def get(self, request):
        pass

    def post(self, request):
        pass


class RegistrationView(View):

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'main/registration.html', context={'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = CustomUser.objects.get(email=form.cleaned_data['email'])
            return HttpResponseRedirect(f'registration/{user.id}')
        return render(request, 'main/registration.html', context={'form': form})


class ConfirmationView(View):

    def get(self, request, id):
        form = ConfirmationForm()
        return render(request, 'main/registration.html', context={'form': form})

    def post(self, request):
        pass
