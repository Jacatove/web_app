import io

import streamlit as st
import qrcode

from services.auth_service import AuthService


auth_service = AuthService()

st.set_page_config(page_title="Auth • Nuu", page_icon="🔐", layout="centered")
st.title("🔐 Sign Up / Sign In")

# ---------- Session ----------
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None


# ---------- UI ----------
if st.session_state.token is None:
    tab_login, tab_signup = st.tabs(["Sign In", "Sign Up"])

    with tab_login:
        with st.form("login_form"):
            u = st.text_input("Username", value=st.session_state.get("prefill_user", ""))
            p = st.text_input("Password", type="password")
            ok = st.form_submit_button("Sign In")
        if ok:
            if not u or not p:
                st.warning("Please enter both username and password.")
            else:
                is_authenticated, details = auth_service.authenticate_user(u, p)

                if is_authenticated:
                    st.session_state.username = u
                    st.session_state.token = details.get('access_token')
                    st.session_state.membership = details.get('membership')
                    st.session_state.is_authenticated = True
                    st.rerun()
                else:
                    st.warning(details)

    with tab_signup:
        with st.form("signup_form"):
            email = st.text_input("Email").strip()
            p1 = st.text_input("Password", type="password")
            p2 = st.text_input("Confirm Password", type="password")
            create = st.form_submit_button("Create Account")
        if create:
            if not email or not p1 or not p2:
                st.warning("Please complete all required fields.")
            elif p1 != p2:
                st.error("Passwords do not match.")
            else:
                signup_msg = auth_service.signup(email, p1)
                st.info(signup_msg)

else:
    st.success(f"Logged in as **{st.session_state.username}**")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Call who am I Endpoint!"):
            response = auth_service.whoami(st.session_state.token)
            st.info(response)
    with col2:
        if st.button("Configure OTP"):
            url = auth_service.configure_otp(st.session_state.token)
            qr = qrcode.QRCode(
                version=1, box_size=10, border=4,  # tweak sizing if you want
                error_correction=qrcode.constants.ERROR_CORRECT_M,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue(), caption="Scan this QR in your authenticator app")

        with st.form("otp-configurar"):
            otp_code = str(int(st.number_input("OTP code", step=1)))
            confirm = st.form_submit_button("Confirmar")
            is_confirm = False

        if confirm:
            is_confirm = auth_service.validate_otp_client_configuration(
                st.session_state.token,
                otp_code,
            )

            if is_confirm:
                st.info("OTP configurado correctamente.")
            else:
                st.info("Intente nuevamente.")

    with col3:
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.username = None
            st.experimental_set_query_params()  # clear URL state, optional
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center;'>© 2025 Nuu | All rights reserved.</p>",
    unsafe_allow_html=True,
)

# import streamlit as st, requests

# API = "api"


# st.title("Sign Up/ Sign In")

# if "token" not in st.session_state:
#     st.session_state.token = None

# if st.session_state.token is None:
#     with st.form("login"):
#         u = st.text_input("Username")
#         p = st.text_input("Password", type="password")
#         ok = st.form_submit_button("Login")
#     if ok:
#         r = requests.post(
#                 f"{API}/login",
#                 data={"username": u, "password": p},
#                 #headers={
#                 #    'Content-Type': 'application/json',
#                 #    'Accept': 'application/json'
#                 #}
#         )
#         if r.ok:
#             st.session_state.token = r.json()["access_token"]
#             st.rerun()
#         else:
#             st.error("Invalid credentials")

# else:
#     st.success("Logged in")
#     if st.button("Call protected"):
#         headers = {"Authorization": f"Bearer {st.session_state.token}"}
#         r = requests.get(f"{API}/protected", headers=headers)
#         st.write(r.json())
#     if st.button("Logout"):
#         st.session_state.token = None
#         st.rerun()
