import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests

from foodsafety import settings
from .models import CustomUser, Product

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
    return render(request, 'core/community_watch.html')

@login_required
def ai_waste_dashboard(request):
    return render(request, 'core/ai_waste_dashboard.html')

@login_required
def ingredient_scanner_dashboard(request):
    return render(request, 'core/ingredient_scanner_dashboard.html')

@login_required
def impact_analytics_dashboard(request):
    return render(request, 'core/impact_analytics_dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'core/admin_dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def donation_portal_dashboard(request):
    products = Product.objects.all().order_by('expire_date')
    total_products = len(products)
    third = total_products // 3
    # Define indices for color coding
    red_end = third
    yellow_end = third * 2
    context = {
        'products': products,
        'red_end': red_end,
        'yellow_end': yellow_end
    }
    return render(request, 'core/donation_portal_dashboard.html', context)

def submit_donation(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        food_items = request.POST.get('food_items')
        pickup_location = request.POST.get('pickup_location')
        messages.success(request, 'Donation submitted successfully!')
        return redirect('core-donation_portal_dashboard')
    return redirect('core/donation_portal_dashboard.html')

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        manufacture_date = request.POST.get('manufacture_date')
        expire_date = request.POST.get('expire_date')
        try:
            Product.objects.create(
                name=name,
                manufacture_date=manufacture_date,
                expire_date=expire_date
            )
            messages.success(request, 'Product added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
        return redirect('core-donation_portal_dashboard')
    return redirect('core/donation_portal_dashboard.html')

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

            # OpenRouter API call
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {'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'}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "meta-llama/llama-3.1-8b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a food safety expert. Provide a concise safety assessment for the given ingredient "
                            "based on the user's medical condition. Return JSON with 'status' (Safe, Caution, Risky), "
                            "'score' (0-100), and 'explanation'. Use double quotes for all strings."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Assess the safety of {ingredient} for someone with {conditions}. "
                            f"Expiration date: {expiration or 'not provided'}. "
                            "Return the response in JSON format with 'status', 'score', and 'explanation' fields. "
                            "Use double quotes for all strings."
                        )
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.2,
                "top_p": 0.9
            }

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                result = response.json()

                # Parse and normalize response
                api_response = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
                safety_data = json.loads(api_response) if isinstance(api_response, str) else api_response

                # Ensure consistent double quotes by re-serializing
                safety_data = json.loads(json.dumps(safety_data, ensure_ascii=False))

                # Ensure response is a list
                safety_response = [safety_data] if isinstance(safety_data, dict) else safety_data

                # Add ingredient to each response item
                for item in safety_response:
                    item['ingredient'] = ingredient

                return JsonResponse(safety_response, safe=False)
            except requests.exceptions.RequestException as e:
                return JsonResponse({
                    "error": f"API request failed: {str(e)}"
                }, status=500)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid request data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)
