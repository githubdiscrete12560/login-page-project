from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from auth import AuthManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize auth manager
auth_manager = AuthManager()

@app.route('/')
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"})

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
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
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not all([email, password, name]):
            return jsonify({"error": "All fields required"}), 400
        
        result = auth_manager.register_user(email, password, name)
        
        if result['success']:
            return jsonify({
                "message": "Registration successful",
                "user": result['user']
            }), 201
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/verify-token', methods=['POST'])
def verify_token():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "No token provided"}), 401
        
        token = auth_header.split(' ')[1]  # Bearer <token>
        result = auth_manager.verify_token(token)
        
        if result['success']:
            return jsonify({
                "message": "Token valid",
                "user": result['user']
            }), 200
        else:
            return jsonify({"error": "Invalid token"}), 401
            
    except Exception as e:
        return jsonify({"error": "Token verification failed"}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)