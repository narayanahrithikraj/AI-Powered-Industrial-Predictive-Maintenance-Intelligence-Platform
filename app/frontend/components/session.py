import streamlit as st
import requests

API_URL = "http://localhost:8000/api"

def login_user(username, password):
    """Hits the FastAPI auth gateway to retrieve a valid secure access token."""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token_data = response.json()
            st.session_state["access_token"] = token_data["access_token"]
            
            # Fetch user profile details to establish permissions
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            # Decode token details via our admin test route to securely parse state
            test_resp = requests.get(f"{API_URL}/admin-only-test", headers=headers)
            if test_resp.status_code == 200:
                st.session_state["user_role"] = "Admin"
                st.session_state["user_name"] = "Administrator"
            else:
                st.session_state["user_role"] = "User"
                st.session_state["user_name"] = username.split("@")[0].capitalize()
                
            st.session_state["authenticated"] = True
            return True
        return False
    except Exception:
        return False

def logout_user():
    """Flushes active authorization tokens to close the workspace session session state safely."""
    st.session_state["authenticated"] = False
    st.session_state["access_token"] = None
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None
    st.rerun()