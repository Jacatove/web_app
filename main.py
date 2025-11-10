import streamlit as st


if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if "token" not in st.session_state:
    st.session_state.token = None

all_pages = [
    st.Page("all_pages/1_landing_page.py", title="Home"),
    st.Page("all_pages/2_auth_page.py", title="Sign Up/Sign In"),
    st.Page("all_pages/3_A_page.py", title="Equipo A"),
    st.Page("all_pages/4_B_page.py", title="Equipo B"),
    st.Page("all_pages/5_C_page.py", title="Equipo Chat"),
]

allowed_pages = [
     all_pages[0],
     all_pages[1],
] if not st.session_state.is_authenticated else all_pages

pg = st.navigation(allowed_pages)
pg.run()
