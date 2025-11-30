import os
import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    if not firebase_admin._apps:
        # Option 1: Load from JSON string in environment variable (Best for Railway/Heroku)
        firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
        
        # DEBUG LOGGING
        if firebase_creds_json:
            print(f"DEBUG: Found FIREBASE_CREDENTIALS_JSON. Length: {len(firebase_creds_json)}")
            print(f"DEBUG: First 20 chars: {firebase_creds_json[:20]}")
        else:
            print("DEBUG: FIREBASE_CREDENTIALS_JSON not found in environment.")

        if firebase_creds_json:
            import json
            try:
                creds_dict = json.loads(firebase_creds_json)
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
                print("Initialized Firebase using FIREBASE_CREDENTIALS_JSON")
                return
            except json.JSONDecodeError as e:
                print(f"Error decoding FIREBASE_CREDENTIALS_JSON: {e}")
            except Exception as e:
                print(f"Error initializing Firebase from JSON string: {e}")
                import traceback
                traceback.print_exc()

        # Option 2: Load from file path
        cred_filename = os.getenv('FIREBASE_ADMIN_CREDENTIALS')
        print(f"DEBUG: FIREBASE_ADMIN_CREDENTIALS env var: {cred_filename}")
        
        # If not in env, try to find the Firebase JSON file in the project root
        if not cred_filename:
            import glob
            firebase_json_files = glob.glob(str(settings.BASE_DIR / '*firebase*.json'))
            if firebase_json_files:
                cred_path = firebase_json_files[0]
                print(f"Using Firebase credentials file: {cred_path}")
            else:
                # If we're here, we failed to find credentials
                # Only raise error if we really need them (e.g. not during build)
                if os.getenv('RAILWAY_ENVIRONMENT'):
                     print("WARNING: Firebase credentials not found. Authentication will fail.")
                     return
                
                raise FileNotFoundError(
                    "Firebase credentials file not found. "
                    "Please add FIREBASE_CREDENTIALS_JSON (content) or FIREBASE_ADMIN_CREDENTIALS (path) to .env"
                )
        else:
            cred_path = os.path.join(settings.BASE_DIR, cred_filename)
        
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")
        
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

initialize_firebase()

def verify_firebase_token(id_token):
    """
    Verify a Firebase ID token and return the decoded token.
    
    Args:
        id_token: The Firebase ID token to verify
        
    Returns:
        dict: Decoded token containing user information
        
    Raises:
        ValueError: If token is invalid
    """
    try:
        print(f"Verifying token: {id_token[:20]}...")
        decoded_token = auth.verify_id_token(id_token)
        print(f"Token verified for UID: {decoded_token.get('uid')}")
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise ValueError(f"Invalid token: {str(e)}")

def get_or_create_user_from_firebase(decoded_token):
    """
    Get or create a Django user based on Firebase token.
    
    Args:
        decoded_token: Decoded Firebase ID token
        
    Returns:
        User: Django user instance
    """
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    firebase_uid = decoded_token['uid']
    email = decoded_token.get('email', '')
    name = decoded_token.get('name', '')
    phone = decoded_token.get('phone_number', '')
    
    # Try to find existing user by firebase_uid
    try:
        user = User.objects.get(firebase_uid=firebase_uid)
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create(
            firebase_uid=firebase_uid,
            email=email,
            name=name,
            phone_number=phone or f'firebase_{firebase_uid[:10]}',  # Fallback if no phone
        )
    
    return user
