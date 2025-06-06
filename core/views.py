import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
import requests
from core.ai.chembarta import show
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Sum
from .models import CustomUser, Donation, Product, CommunityReport, Comment

def index(request):
    if request.user.is_authenticated:
        return redirect('core-dashboard')  # or 'core-donation_portal_dashboard'
    return render(request, 'core/landing.html')  # Create this template for your landing page

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # Redirect admin (superuser or staff) to impact analytics dashboard
            if user.is_superuser or user.is_staff:
                return redirect('core-impact_analytics_dashboard')
            # Otherwise, redirect to normal dashboard
            next_url = request.GET.get('next', 'core-dashboard')
            return redirect(next_url)
        else:
            return render(request, 'core/login.html', {
                'user_login_error': 'Invalid email or password'
            })
    return render(request, 'core/login.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'core/signup.html', {
                'user_signup_error': 'Email already exists',
            })

        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name,
        )
        login(request, user)  # Now uses django.contrib.auth.login
        next_url = request.GET.get('next', 'core-about-user')
        return redirect(next_url)

    return render(request, 'core/signup.html')
@login_required
def user_about(request):
    if request.method == 'POST':
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        # Get all selected medical conditions as a list
        medical_conditions = request.POST.getlist('medical_condition')
        # Join them as a comma-separated string
        request.user.gender = gender
        request.user.dob = dob
        request.user.medical_condition = ', '.join(medical_conditions)
        request.user.save()
        return redirect('core-dashboard')
    return render(request, 'core/about_user.html')
@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

@login_required
def community_watch(request):
    if request.method == 'POST':
        # Save the new report
        CommunityReport.objects.create(
            reporter_name=request.POST.get('reporter_name'),
            item_name=request.POST.get('item_name'),
            location=request.POST.get('location'),
            issue_type=request.POST.get('issue_type'),
            description=request.POST.get('description'),
            photo=request.FILES.get('photo')
        )
        return redirect('core-community_watch')  # Redirect to clear POST and avoid resubmission

    reports = CommunityReport.objects.all().order_by('-created_at')
    return render(request, 'core/community_watch.html', {
        'reports': reports,
        'user': request.user,
    })

@login_required
def ai_waste_dashboard(request):
    return render(request, 'core/ai_waste_dashboard.html')

@login_required
def ingredient_scanner_dashboard(request):
    return render(request, 'core/ingredient_scanner_dashboard.html')

@user_passes_test(lambda u: u.is_superuser or u.is_staff or getattr(u, 'is_admin', False))
def impact_analytics_dashboard(request):
    # Total food waste reduced (sum of donated product weights)
    food_waste_reduced = Product.objects.filter(status='Donated').count()
    # Total donations matched
    donations_matched = Donation.objects.count()

    # Total community reports
    community_reports = CommunityReport.objects.count()

    # Safe ingredients scanned (replace with your logic if you have a model for scans)
    safe_ingredients_scanned = 26  # Placeholder, update if you track scans

    # Expiry trends (example: number of products expiring each day for the last 7 days)
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    expiry_trends = [
        Product.objects.filter(expire_date=today - timedelta(days=i)).count()
        for i in reversed(range(7))
    ]

    # Status breakdown
    status_breakdown = {
        'Available': Product.objects.filter(status='Available').count(),
        'Donated': Product.objects.filter(status='Donated').count(),
        'Thrown': Product.objects.filter(status='Thrown').count(),
    }

    # Flags by type (if you have a 'flag' field, otherwise skip or adjust)
    flags_by_type = {
        'Expired': Product.objects.filter(expire_date__lt=today, status='Available').count(),
        # Add more flag logic if you have more flag types
    }

    context = {
        'food_waste_reduced': food_waste_reduced,
        'donations_matched': donations_matched,
        'community_reports': community_reports,
        'safe_ingredients_scanned': safe_ingredients_scanned,
        'expiry_trends': expiry_trends,
        'status_breakdown': status_breakdown,
        'flags_by_type': flags_by_type,
    }
    return render(request, 'core/impact_analytics_dashboard.html', context)

@login_required
def admin_dashboard(request):
    return render(request, 'core/admin_dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def donation_portal_dashboard(request):
    search_query = request.GET.get('search', '')
    if search_query:
        products = Product.objects.filter(
            user=request.user,
            name__icontains=search_query,
            status='Available'
        ).order_by('expire_date')
    else:
        products = Product.objects.filter(
            user=request.user,
            status='Available'
        ).order_by('expire_date')
    total_products = products.count()
    third = total_products // 3
    red_end = third
    yellow_end = third * 2

    # Expiring soon: count of products in the "red" section
    expiring_soon_count = red_end

    # Recently Donated: count of donations in the last 7 days
    last_week = timezone.now() - timedelta(days=7)
    donation_count = Donation.objects.filter(
        user=request.user,
        created_at__gte=last_week
    ).count()

    context = {
        'products': products,
        'red_end': red_end,
        'yellow_end': yellow_end,
        'expiring_soon_count': expiring_soon_count,
        'donation_count': donation_count,
    }
    return render(request, 'core/donation_portal_dashboard.html', context)
@login_required
def donation_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        try:
            donor_name = request.POST.get('donor_name')
            contact_email = request.POST.get('contact_email')
            contact_number = request.POST.get('contact')
            pickup_address = request.POST.get('address')
            pickup_datetime = request.POST.get('pickup_datetime')
            notes = request.POST.get('notes', '')

            donation = Donation(
                user=request.user,
                product=product,
                donor_name=donor_name,
                contact_email=contact_email,
                contact_number=contact_number,
                pickup_address=pickup_address,
                pickup_datetime=pickup_datetime,
                notes=notes
            )
            donation.full_clean()
            donation.save()

            product.status = 'Donated'
            product.save()

            messages.success(request, f"Donation of {product.name} successfully submitted!")
            return redirect('donation-history')  # Redirect to donation history

        except ValidationError as e:
            messages.error(request, f"Error: {', '.join(e.messages)}")
            return render(request, 'core/donation_details.html', {'product': product})

    return render(request, 'core/donation_details.html', {'product': product})

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        manufacture_date = request.POST.get('manufacture_date')
        expire_date = request.POST.get('expire_date')
        try:
            Product.objects.create(
                user=request.user,
                name=name,
                manufacture_date=manufacture_date,
                expire_date=expire_date,
                status='Available'
            )
            messages.success(request, 'Product added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
        return redirect('core-donation_portal_dashboard')
    return redirect('core/donation_portal_dashboard.html')


def throw_product(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to throw a product.')
        return redirect('login')

    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == 'POST':
        try:
            product.status = 'Thrown'
            product.save()
            messages.success(request, f'{product.name} marked as thrown!')
        except Exception as e:
            messages.error(request, f'Error throwing product: {str(e)}')
        return redirect('core-donation_portal_dashboard')
    return render(request, 'core/confirm_throw.html', {'product': product})



def profile(request):
    user = request.user
    medical_condition_str = getattr(user, "medical_condition", "")
    if medical_condition_str:
        medical_condition_list = [c.strip() for c in medical_condition_str.split(",") if c.strip()]
    else:
        medical_condition_list = []
    context = {
        "user": user,
        "gender": getattr(user, "gender", ""),
        "dob": getattr(user, "dob", ""),
        "medical_condition": medical_condition_str,
        "medical_condition_list": medical_condition_list,
    }
    return render(request, "core/profile.html", context)

@login_required
def check_safety(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ingredient = data.get('ingredient')
            expiration = data.get('expiration')
            conditions = data.get('conditions')

            # Try to use as E Number first, fallback to ingredient
            result = show(ingredient)  # If not found, show() will use ingredient if provided
            # Return all fields from chembarta.py as-is
            response = [result]
            print(response)

            return JsonResponse(response, safe=False)
        except Exception as e:
            print(f"Error in check_safety: {e}")
            return JsonResponse({'error': 'An error occurred while checking safety.'}, status=500)

def donation_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        # Process donation details here
        # ...
        return redirect('core-donation_portal_dashboard')
    return render(request, 'core/donation_details.html', {'product': product})

def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        messages.success(request, 'Product deleted successfully!')
    return redirect('core-donation_portal_dashboard')

def add_comment(request, report_id):
    if request.method == 'POST':
        report = get_object_or_404(CommunityReport, id=report_id)
        text = request.POST.get('comment')
        if text and request.user.is_authenticated:
            Comment.objects.create(
                report=report,
                user=request.user,
                text=text
            )
    return redirect('core-community_watch')
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import CommunityReport

@login_required
def delete_community_report(request, report_id):
    report = get_object_or_404(CommunityReport, id=report_id)
    if request.user.is_superuser or report.reporter_name == request.user.get_full_name() or report.reporter_name == request.user.username:
        report.delete()
    return redirect('core-community_watch')

from django.contrib.auth.decorators import login_required
from .models import Donation

@login_required
def donation_history(request):
    donations = Donation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/donation_history.html', {'donations': donations})