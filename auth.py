import jwt
import hashlib
import datetime
from supabase import create_client, Client
from config import Config

class AuthManager:
    def __init__(self):
        self.supabase: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self, user_id: str, email: str) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            
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
    
    def authenticate_user(self, email: str, password: str) -> dict:
        """Authenticate user credentials"""
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
            return {'success': False, 'error': 'Authentication failed'}
    
    def register_user(self, email: str, password: str, name: str) -> dict:
        """Register new user"""
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
            return {'success': False, 'error': 'Registration failed'}