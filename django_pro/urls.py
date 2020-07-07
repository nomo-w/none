"""test_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from test.views import Test1, Test2
from pay.views import Deposit, Callback
from game.views import Login, Withdraw, GetWallet
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('test1/', Test1.as_view()),
    path('test2/', Test2),
    path('callback/', Callback.as_view()),
    path('deposit/', csrf_exempt(Deposit.as_view())),
    path('getGame/', csrf_exempt(Login.as_view())),
    path('withdraw/', csrf_exempt(Withdraw.as_view())),
    path('getWallet/', csrf_exempt(GetWallet.as_view())),
]
