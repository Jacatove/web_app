import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Nuu | Welcome",
    page_icon="✨",
    layout="centered",
)

# Main section
st.title("👋 Welcome to Nuu")
st.subheader("We’re glad you’re here at **nuu.com.co**")

st.write("""
At **Nuu**, we believe in innovation, creativity, and connection.
Explore our world and discover how we can grow your MONEY together.
""")

if st.button("🚀 Sign Up/Sign In"):
    st.success("Thanks for visiting! We’re excited to have you here.")

    st.switch_page("all_pages/2_auth_page.py")
    st.stop()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center;'>© 2025 Nuu | All rights reserved.</p>",
    unsafe_allow_html=True,
)