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
        cred_filename = os.getenv('FIREBASE_ADMIN_CREDENTIALS')
        
        # If not in env, try to find the Firebase JSON file in the project root
        if not cred_filename:
            import glob
            firebase_json_files = glob.glob(str(settings.BASE_DIR / '*firebase*.json'))
            if firebase_json_files:
                cred_path = firebase_json_files[0]
                print(f"Using Firebase credentials file: {cred_path}")
            else:
                raise FileNotFoundError(
                    "Firebase credentials file not found. "
                    "Please add FIREBASE_ADMIN_CREDENTIALS to .env or place the Firebase JSON file in the project root."
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
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
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
