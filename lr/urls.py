from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name = 'register'),
    path('login', views.login, name = 'login'),
    path('customer', views.customer, name = 'customer')
] 