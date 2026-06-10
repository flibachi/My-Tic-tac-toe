from flask import Blueprint, request, jsonify
from domain.service.auth_service import AuthService
from web.model.web_auth_model import SignUpRequest

auth_bp = Blueprint("auth", __name__)
_auth_service = AuthService()


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    POST /auth/register
    Body: {"login": "...", "password": "..."}
    Returns 201 on success, 400 if login already exists.
    """
    data = request.get_json() or {}
    login = data.get("login", "").strip()
    password = data.get("password", "")

    if not login or not password:
        return jsonify({"error": "login and password are required"}), 400

    sign_up = SignUpRequest(login=login, password=password)
    success = _auth_service.register(sign_up)
    if success:
        return jsonify({"message": "User registered successfully"}), 201
    return jsonify({"error": "Login already taken"}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /auth/login
    Expects Basic Auth header: Authorization: Basic <base64(login:password)>
    Returns {"user_id": "<uuid>"} on success, 401 on failure.
    """
    auth_header = request.headers.get("Authorization", "")
    user_id = _auth_service.authorize(auth_header)
    if user_id:
        return jsonify({"user_id": user_id}), 200
    return jsonify({"error": "Invalid credentials"}), 401
