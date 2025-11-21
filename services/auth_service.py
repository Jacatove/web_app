import base64
import json

import requests

from settings import API_BASE


class AuthService:
    """Service for authentication and registration."""


    @staticmethod
    def authenticate_user(username: str, password: str):
        """
        Authenticate user against API.

        Args:
            password (str)
            username (email)

        Returns:
            Token: Access token and metadata.

        Raises:
            HTTPException: If credentials are invalid or account does not exist.
        """
        r = requests.post(
            f"{API_BASE}/account/signin",
            data={"username": username, "password": password},
            headers={"Accept": "application/json"},
        )

        if not r.ok:
            return False, r.json().get("detail")

        token = r.json().get("access_token")

        # 1) Take the payload part of the JWT
        payload_part = token.split('.')[1]

        # 2) Add padding so length is a multiple of 4
        padding_needed = -len(payload_part) % 4
        payload_part += "=" * padding_needed
        payload_bytes = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(payload_bytes)

        return True, {
            "access_token": token,
            "token_type": "bearer",
            "membership": payload.get('membership')
        }



    @staticmethod
    def signup(email: str, password: str):

        r = requests.post(
            f"{API_BASE}/account/signup",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

        msg = ""

        if r.ok:
            msg = "Account created! You can sign in now."
        else:
            try:
                msg = r.json().get("detail", "Sign up failed")
            except Exception:
                msg = r.text or "Sign up failed"

        return msg


    @staticmethod
    def whoami(acess_token: str):
        headers = {"Authorization": f"Bearer {acess_token}"}
        return requests.get(f"{API_BASE}/whoami", headers=headers).json()


    @staticmethod
    def configure_otp(access_token: str):
        headers = {"Authorization": f"Bearer {access_token}"}
        return requests.get(f"{API_BASE}/otp", headers=headers).json().get("otpauth_url")

    @staticmethod
    def validate_otp_client_configuration(access_token: str, otp_code: str):
        return requests.post(
            f"{API_BASE}/confirm-otp",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={"otp_code": otp_code},
        ).json()
