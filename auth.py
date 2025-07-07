import os
import jwt
import hashlib
import datetime
from supabase import create_client, Client

class AuthManager:
    def __init__(self):
        # Get environment variables
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        
        # Validate environment variables
        if not supabase_url:
            raise ValueError("SUPABASE_URL environment variable is not set")
        if not supabase_key:
            raise ValueError("SUPABASE_KEY environment variable is not set")
        
        # Validate URL format
        if not supabase_url.startswith('https://'):
            raise ValueError(f"Invalid SUPABASE_URL format: {supabase_url}")
        
        # Validate key format (should start with 'eyJ')
        if not supabase_key.startswith('eyJ'):
            raise ValueError("Invalid SUPABASE_KEY format (should start with 'eyJ')")
        
        print(f"Connecting to Supabase: {supabase_url[:50]}...")
        
        try:
            # Create Supabase client with minimal options
            self.supabase: Client = create_client(supabase_url, supabase_key)
            print("✅ Supabase client created successfully")
        except Exception as e:
            print(f"❌ Failed to create Supabase client: {e}")
            raise
    
    def authenticate_user(self, email: str, password: str) -> dict:
        try:
            hashed_password = self.hash_password(password)
            
            response = self.supabase.table('users').select('*').eq('email', email).eq('password', hashed_password).execute()
            
            if response.data:
                user = response.data[0]
                token = self.generate_token(user['id'], user['email'])
                
                return {
                    'success': True,
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'name': user['name']
                    }
                }
            else:
                return {'success': False, 'error': 'Invalid credentials'}
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return {'success': False, 'error': 'Authentication failed'}
    
    def register_user(self, email: str, password: str, name: str) -> dict:
        try:
            # Check if user exists
            existing_user = self.supabase.table('users').select('*').eq('email', email).execute()
            
            if existing_user.data:
                return {'success': False, 'error': 'User already exists'}
            
            # Hash password and create user
            hashed_password = self.hash_password(password)
            
            response = self.supabase.table('users').insert({
                'email': email,
                'password': hashed_password,
                'name': name,
                'created_at': datetime.datetime.utcnow().isoformat()
            }).execute()
            
            if response.data:
                user = response.data[0]
                return {
                    'success': True,
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'name': user['name']
                    }
                }
            else:
                return {'success': False, 'error': 'Registration failed'}
                
        except Exception as e:
            print(f"Registration error: {e}")
            return {'success': False, 'error': 'Registration failed'}
    
    def verify_token(self, token: str) -> dict:
        try:
            jwt_secret = os.environ.get('JWT_SECRET')
            if not jwt_secret:
                return {'success': False, 'error': 'JWT_SECRET not configured'}
            
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            
            # Get user from database
            response = self.supabase.table('users').select('*').eq('id', payload['user_id']).execute()
            
            if response.data:
                user = response.data[0]
                return {
                    'success': True,
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'name': user['name']
                    }
                }
            else:
                return {'success': False, 'error': 'User not found'}
                
        except jwt.ExpiredSignatureError:
            return {'success': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'success': False, 'error': 'Invalid token'}
        except Exception as e:
            print(f"Token verification error: {e}")
            return {'success': False, 'error': 'Token verification failed'}
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self, user_id: str, email: str) -> str:
        """Generate JWT token"""
        jwt_secret = os.environ.get('JWT_SECRET')
        if not jwt_secret:
            raise ValueError("JWT_SECRET environment variable is not set")
        
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        return jwt.encode(payload, jwt_secret, algorithm='HS256')
