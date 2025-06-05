from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from core.views import call_openrouter_api, get_fallback_response

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
                    If you're unsure about something, acknowledge the limitation and suggest consulting a food safety expert.
                    
                    Keep your responses concise and focused on the user's question.
                    Limit your response to 2-3 sentences maximum."""
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
            
            try:
                # Use a lower token limit to stay within credit limits
                result = call_openrouter_api(
                    messages=messages,
                    model="anthropic/claude-3-opus:beta",
                    max_tokens=200,  # Reduced token limit
                    temperature=0.7
                )
                
                if not result or 'choices' not in result or not result['choices']:
                    logger.error("Invalid response format from API")
                    return JsonResponse(get_fallback_response())
                
                return JsonResponse(result)
                
            except Exception as e:
                error_message = str(e)
                logger.error(f"Error in get_response: {error_message}")
                
                # Provide specific error messages based on the error type
                if "401" in error_message:
                    return JsonResponse({
                        'error': 'Authentication failed. Please contact support.'
                    }, status=401)
                elif "402" in error_message:
                    return JsonResponse({
                        'error': 'Service temporarily unavailable. Please try again later.'
                    }, status=402)
                elif "429" in error_message:
                    return JsonResponse({
                        'error': 'Too many requests. Please wait a moment and try again.'
                    }, status=429)
                else:
                    return JsonResponse(get_fallback_response())
            
        except Exception as e:
            logger.error(f"Unexpected error in get_response: {str(e)}")
            return JsonResponse(get_fallback_response())
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
