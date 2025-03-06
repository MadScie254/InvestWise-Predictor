from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from .models import BlacklistedToken  # Custom model to store blacklisted tokens

# ===========================
# 1. Custom JWT Authentication Class
# ===========================

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class to enhance security and functionality.
    - Adds token blacklisting support.
    - Validates token expiration and integrity.
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a tuple of (user, token).
        """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            # Validate the token
            validated_token = self.get_validated_token(raw_token)

            # Check if the token is blacklisted
            if BlacklistedToken.objects.filter(token=raw_token.decode('utf-8')).exists():
                raise AuthenticationFailed(_("Token is blacklisted"), code="token_blacklisted")

            # Get the user associated with the token
            user = self.get_user(validated_token)
            return user, validated_token

        except TokenError as e:
            raise InvalidToken(e.args[0])

    def get_validated_token(self, raw_token):
        """
        Validate the token and ensure it meets all requirements.
        """
        try:
            # Use UntypedToken to validate the token without decoding it fully
            UntypedToken(raw_token)
        except (InvalidToken, TokenError) as e:
            raise InvalidToken(_("Token is invalid or expired"))

        return super().get_validated_token(raw_token)


# ===========================
# 2. Token Blacklisting Utility
# ===========================

class TokenBlacklistService:
    """
    Service to handle token blacklisting.
    - Used for logging out users or revoking tokens.
    """

    @staticmethod
    def blacklist_token(token: str):
        """
        Add a token to the blacklist.
        """
        BlacklistedToken.objects.create(token=token)

    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """
        Check if a token is blacklisted.
        """
        return BlacklistedToken.objects.filter(token=token).exists()


# ===========================
# 3. Role-Based Authentication
# ===========================

class RoleBasedAuthentication(CustomJWTAuthentication):
    """
    Custom authentication class for role-based access control.
    - Ensures users have specific roles/permissions to access certain endpoints.
    """

    def authenticate(self, request):
        """
        Authenticate the request and enforce role-based access control.
        """
        user, token = super().authenticate(request)

        # Example: Check if the user has a specific role (e.g., 'admin')
        required_role = getattr(request, "required_role", None)
        if required_role and not user.has_role(required_role):  # Assuming a `has_role` method in the User model
            raise AuthenticationFailed(_("You do not have permission to access this resource."), code="permission_denied")

        return user, token


# ===========================
# 4. Custom User Model Integration
# ===========================

User = get_user_model()

def authenticate_user(email: str, password: str):
    """
    Authenticate a user by email and password.
    - Returns the user instance if authentication is successful.
    - Raises an exception if authentication fails.
    """
    user = User.objects.filter(email=email).first()
    if user is None or not user.check_password(password):
        raise AuthenticationFailed(_("Invalid email or password"), code="invalid_credentials")
    return user


# ===========================
# 5. Logging and Error Handling
# ===========================

import logging

logger = logging.getLogger(__name__)

def log_authentication_attempt(user, success: bool):
    """
    Log authentication attempts for monitoring and auditing.
    """
    status = "SUCCESS" if success else "FAILURE"
    logger.info(f"Authentication attempt by user {user.email}: {status}")
