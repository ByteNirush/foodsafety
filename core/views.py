from django.shortcuts import render

def login(request):
    return render(request, 'core/login.html')

def signup(request):
    return render(request, 'core/signup.html')

def dashboard(request):
    return render(request, 'core/dashboard.html')

def community_watch(request):
    return render(request, 'core/community_watch.html')

def ai_waste_dashboard(request):
    return render(request, 'core/ai_waste_dashboard.html')

def ingredient_scanner_dashboard(request):
    return render(request, 'core/ingredient_scanner_dashboard.html')

