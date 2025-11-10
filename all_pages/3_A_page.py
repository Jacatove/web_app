import streamlit as st

st.title("Equipo A")

'FREE'
'PREMIUM'
st.session_state.token = "token inventado"
st.session_state.is_authenticated = True
st.session_state.membership = 'PREMIUM'

st.info(
    f"{st.session_state.token}{st.session_state.is_authenticated}{st.session_state.membership}"
)