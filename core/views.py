from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser

def index(request):
    return render(request, 'core/login.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'core-dashboard' if not user.is_admin else 'core-admin_dashboard')
            return redirect(next_url)
        else:
            return render(request, 'core/login.html', {
                'user_login_error': 'Invalid email or password' if not user or not user.is_admin else None,
                'admin_login_error': 'Invalid admin email or password' if user and user.is_admin else None
            })
    return render(request, 'core/login.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        admin_code = request.POST.get('admin_code', None)
        is_admin = bool(admin_code)

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'core/signup.html', {
                'user_signup_error': 'Email already exists' if not is_admin else None,
                'admin_signup_error': 'Email already exists' if is_admin else None
            })

        if is_admin and admin_code != 'rojan123':  # Replace with your secure admin code
            return render(request, 'core/signup.html', {'admin_signup_error': 'Invalid admin code'})

        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name,
            is_admin=is_admin,
            admin_code=admin_code if is_admin else None
        )
        login(request, user)  # Now uses django.contrib.auth.login
        next_url = request.GET.get('next', 'core-admin_dashboard' if is_admin else 'core-about-user')
        return redirect(next_url)

    return render(request, 'core/signup.html')
def user_about(request):
    return render(request, 'core/about_user.html')
@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

@login_required
def community_watch(request):
    return render(request, 'core/community_watch.html')

@login_required
def ai_waste_dashboard(request):
    return render(request, 'core/ai_waste_dashboard.html')

@login_required
def ingredient_scanner_dashboard(request):
    return render(request, 'core/ingredient_scanner_dashboard.html')

@login_required
def donation_portal_dashboard(request):
    return render(request, 'core/donation_portal_dashboard.html')

@login_required
def impact_analytics_dashboard(request):
    return render(request, 'core/impact_analytics_dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'core/admin_dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('index')