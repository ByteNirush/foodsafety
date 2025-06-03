from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='core-login'),
    path('signup/', views.signup, name='core-signup'),
]