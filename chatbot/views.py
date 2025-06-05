from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from core.views import call_openrouter_api

logger = logging.getLogger(__name__)

# Create your views here.

def chatbot_view(request):
    return render(request, 'chatbot/chatbot.html')

@login_required
def get_response(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if not message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a Food Safety Assistant, an expert in food safety, handling, and regulations. 
                    Your role is to provide accurate, helpful information about:
                    - Food handling and storage best practices
                    - Food safety regulations and compliance
                    - Preventing foodborne illnesses
                    - Restaurant food safety guidelines
                    - Home food safety tips
                    - Food waste reduction
                    - Food safety certifications
                    - Food safety training requirements
                    
                    Always provide practical, actionable advice and cite relevant regulations when applicable.
                    If you're unsure about something, acknowledge the limitation and suggest consulting a food safety expert."""
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
            
            result = call_openrouter_api(
                messages=messages,
                model="anthropic/claude-3-opus:beta",
                max_tokens=300,
                temperature=0.7
            )
            
            return JsonResponse(result)
            
        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return JsonResponse({
                'error': 'Failed to get response from AI service. Please try again.'
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
