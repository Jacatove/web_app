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

        if r.ok:
            token = r.json().get("access_token")

        return {
            "access_token": token,
            "token_type": "bearer",
            "membership": json.loads(
                base64.urlsafe_b64decode(token.split('.')[1])
            ).get('membership')
        }



    @staticmethod
    def signup(email: str, password: str):

        r = requests.post(
            f"{API_BASE}/account/signup",
            json={"username": email, "password": password},
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
        return requests.get(f"{API_BASE}/otp", headers=headers).json().get("url")


