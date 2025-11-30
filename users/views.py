from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .firebase_auth import verify_firebase_token, get_or_create_user_from_firebase
import os

def get_firebase_config():
    """Get Firebase configuration from environment variables."""
    return {
        'api_key': os.getenv('FIREBASE_API_KEY'),
        'auth_domain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'project_id': os.getenv('FIREBASE_PROJECT_ID'),
        'storage_bucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messaging_sender_id': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'app_id': os.getenv('FIREBASE_APP_ID'),
    }

def register(request):
    """Render the Firebase registration page."""
    return render(request, 'users/register.html', {'firebase_config': get_firebase_config()})

def login_page(request):
    """Render the Firebase login page."""
    return render(request, 'users/login.html', {'firebase_config': get_firebase_config()})

@csrf_exempt
@require_http_methods(["POST"])
def firebase_auth(request):
    """
    Handle Firebase authentication.
    Receives the Firebase ID token from the frontend,
    verifies it, and creates/logs in the Django user.
    """
    try:
        data = json.loads(request.body)
        id_token = data.get('idToken')
        
        if not id_token:
            return JsonResponse({'error': 'No token provided'}, status=400)
        
        # Verify the Firebase token
        decoded_token = verify_firebase_token(id_token)
        
        # Get or create Django user
        user = get_or_create_user_from_firebase(decoded_token)
        
        # Log the user into Django session
        django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        return JsonResponse({
            'success': True,
            'redirect': '/'
        })
        
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=401)
    except Exception as e:
        return JsonResponse({'error': 'Authentication failed'}, status=500)

def logout_view(request):
    """Logout the user."""
    from django.contrib.auth import logout
    logout(request)
    return redirect('users:login')
