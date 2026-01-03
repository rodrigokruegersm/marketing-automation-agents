"""
Adlytics Authentication Module
Secure password-based access control
"""

import streamlit as st
import hashlib
import hmac


def check_password() -> bool:
    """
    Returns True if the user has entered the correct password.
    Shows a login screen if not authenticated.
    """

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(
            hashlib.sha256(st.session_state["password"].encode()).hexdigest(),
            hashlib.sha256(get_password().encode()).hexdigest()
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    def get_password() -> str:
        """Get password from secrets or environment"""
        try:
            return st.secrets.get("DASHBOARD_PASSWORD", "adlytics2026")
        except:
            import os
            return os.getenv("DASHBOARD_PASSWORD", "adlytics2026")

    # First run or logout
    if "password_correct" not in st.session_state:
        render_login_page(password_entered)
        return False

    # Password was entered but incorrect
    if not st.session_state["password_correct"]:
        render_login_page(password_entered)
        st.error("Senha incorreta. Tente novamente.")
        return False

    # Password correct
    return True


def render_login_page(callback):
    """Render the login page with Adlytics branding"""

    # Custom CSS for login page
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .stApp {
            background: linear-gradient(135deg, #0A1628 0%, #1E293B 100%) !important;
        }

        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 3rem;
            background: #FFFFFF;
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            text-align: center;
        }

        .login-logo {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            font-family: 'Inter', sans-serif;
        }

        .login-logo-ad {
            color: #0066FF;
        }

        .login-logo-lytics {
            color: #0A1628;
        }

        .login-tagline {
            color: #64748B;
            font-size: 1rem;
            margin-bottom: 2rem;
        }

        .login-title {
            color: #1E293B;
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }

        /* Override Streamlit input styles */
        .stTextInput > div > div > input {
            background: #F8FAFC !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 0.75rem 1rem !important;
            font-size: 1rem !important;
            color: #0A1628 !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: #0066FF !important;
            box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1) !important;
        }

        .stButton > button {
            width: 100%;
            background: #0066FF !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            margin-top: 1rem !important;
            transition: all 0.2s !important;
        }

        .stButton > button:hover {
            background: #0052CC !important;
            transform: translateY(-1px) !important;
        }

        .login-footer {
            margin-top: 2rem;
            color: #94A3B8;
            font-size: 0.875rem;
        }

        /* Hide default Streamlit elements */
        #MainMenu, footer, header { visibility: hidden !important; }

        /* Center the form */
        [data-testid="stForm"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<div style='height: 10vh'></div>", unsafe_allow_html=True)

    # Login card
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-logo">
                <span class="login-logo-ad">Ad</span><span class="login-logo-lytics">lytics</span>
            </div>
            <div class="login-tagline">Intelligence for Scale</div>
            <div class="login-title">Acesso ao Dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        # Password input
        st.text_input(
            "Senha",
            type="password",
            key="password",
            on_change=callback,
            label_visibility="collapsed",
            placeholder="Digite a senha de acesso"
        )

        # Login button
        st.button("Entrar", on_click=callback, use_container_width=True)

        st.markdown("""
        <div class="login-footer">
            Acesso restrito a usuarios autorizados
        </div>
        """, unsafe_allow_html=True)


def logout():
    """Logout the current user"""
    if "password_correct" in st.session_state:
        del st.session_state["password_correct"]
    st.rerun()
