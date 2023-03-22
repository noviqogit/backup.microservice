"""microservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from main.views import PhoneView, LoginView, LogoutView, RegistrationView, ConfirmationView, TelegramView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login', LoginView.as_view(), name='login'),
    # path('logout', LogoutView.as_view(), name='logout'),
    path('registration', RegistrationView.as_view(), name='registration'),
    path('activate/<uidb64>/<token>', ConfirmationView.as_view(), name='activate'),
    path('', PhoneView.as_view(), name='phone'),
    path('<str:phone>', TelegramView.as_view(), name='telegram'),
    path('download', PhoneView.as_view(), name='download'),
]

# from django.contrib.auth import views
