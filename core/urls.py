from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='core-dashboard'),
    path('login/', views.login, name='core-login'),
    path('signup/', views.signup, name='core-signup'),
    path('community-watch/', views.community_watch, name='core-community-watch'),
    path('ai-waste-dashboard/', views.ai_waste_dashboard, name='core-ai-waste-dashboard'),
    path('ingredient-scanner-dashboard/', views.ingredient_scanner_dashboard, name='core-ingredient-scanner-dashboard'),
]