from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='core-login'),  # Updated to user_login
    path('signup/', views.signup, name='core-signup'),
    path('user-about/', views.user_about, name='core-about-user'),
    path('dashboard/', views.dashboard, name='core-dashboard'),
    path('community-watch/', views.community_watch, name='core-community_watch'),
    path('ai-waste-dashboard/', views.ai_waste_dashboard, name='core-ai_waste_dashboard'),
    path('ingredient-scanner-dashboard/', views.ingredient_scanner_dashboard, name='core-ingredient_scanner_dashboard'),
    path('donation-portal-dashboard/', views.donation_portal_dashboard, name='core-donation_portal_dashboard'),
    path('impact-analytics-dashboard/', views.impact_analytics_dashboard, name='core-impact_analytics_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='core-admin_dashboard'),
    path('logout/', views.logout_view, name='core-logout'),
    path('donation/submit/', views.submit_donation, name='donation-submit'),
    path('product/add/', views.add_product, name='add-product'),
    path('profile/', views.profile, name='core-profile'),
    path('ingredient_scanner_dashboard/', views.check_safety, name='core-check_safety'),
]