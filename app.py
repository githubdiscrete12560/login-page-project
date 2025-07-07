import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def health_check():
    # Debug environment variables
    return jsonify({
        "status": "healthy",
        "message": "API is running",
        "environment_check": {
            "SUPABASE_URL": "✅ Set" if os.environ.get('SUPABASE_URL') else "❌ Missing",
            "SUPABASE_KEY": "✅ Set" if os.environ.get('SUPABASE_KEY') else "❌ Missing",
            "SECRET_KEY": "✅ Set" if os.environ.get('SECRET_KEY') else "❌ Missing",
            "JWT_SECRET": "✅ Set" if os.environ.get('JWT_SECRET') else "❌ Missing"
        },
        "supabase_url_preview": os.environ.get('SUPABASE_URL', 'NOT SET')[:50] + "..." if os.environ.get('SUPABASE_URL') else "NOT SET"
    })

# Safer import with error handling
try:
    from auth import AuthManager
    auth_manager = AuthManager()
    print("✅ AuthManager initialized successfully")
except Exception as e:
    print(f"❌ AuthManager initialization failed: {e}")
    auth_manager = None

@app.route('/api/login', methods=['POST'])
def login():
    if not auth_manager:
        return jsonify({"error": "Authentication service unavailable"}), 500
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        # Test authentication
        result = auth_manager.authenticate_user(email, password)
        
        if result['success']:
            return jsonify({
                "message": "Login successful",
                "token": result['token'],
                "user": result['user']
            }), 200
        else:
            return jsonify({"error": result['error']}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
