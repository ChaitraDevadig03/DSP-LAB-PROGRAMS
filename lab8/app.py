import streamlit as st
import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import datetime

# JWT Secret Key
SECRET_KEY = "your-secret-key"

# Initialize session state
if 'private_key' not in st.session_state:
    st.session_state.private_key = None
if 'public_key' not in st.session_state:
    st.session_state.public_key = None
if 'signature' not in st.session_state:
    st.session_state.signature = None
if 'token' not in st.session_state:
    st.session_state.token = None
if 'users' not in st.session_state:
    st.session_state.users = []

st.title("Digital Signatures, Authentication & Authorization Demo")

# Sidebar for navigation
option = st.sidebar.selectbox("Choose Section", ["Digital Signatures", "Authentication & Authorization"])

if option == "Digital Signatures":
    st.header("RSA Digital Signature Generation and Verification")

    # Generate keys
    if st.button("Generate RSA Keys"):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        st.session_state.private_key = private_key
        st.session_state.public_key = public_key
        st.success("RSA Keys generated successfully!")

    if st.session_state.private_key:
        message = st.text_area("Enter message to sign")
        if st.button("Sign Message"):
            signature = st.session_state.private_key.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            st.session_state.signature = signature
            st.success("Message signed!")

        if st.session_state.signature:
            verify_message = st.text_area("Enter message to verify")
            if st.button("Verify Signature"):
                try:
                    st.session_state.public_key.verify(
                        st.session_state.signature,
                        verify_message.encode(),
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    st.success("Signature is valid!")
                except:
                    st.error("Signature is invalid!")

elif option == "Authentication & Authorization":
    st.header("Authentication and Authorization Simulation")

    # Registration form
    st.subheader("Register New User")
    with st.expander("Registration Form"):
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        if st.button("Register"):
            if reg_password != reg_confirm:
                st.error("Passwords do not match")
            elif any(u['username'] == reg_username for u in st.session_state.users):
                st.error("Username already exists")
            else:
                st.session_state.users.append({'username': reg_username, 'password': reg_password})
                st.success("Registered successfully!")

    # Login form
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = next((u for u in st.session_state.users if u['username'] == username and u['password'] == password), None)
        if user:
            payload = {
                "user": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            st.session_state.token = token
            st.success("Logged in successfully! JWT Token generated.")
        else:
            st.error("Invalid credentials")

    if st.session_state.token:
        st.write("Your JWT Token:", st.session_state.token)

        # Simulate secure API call
        if st.button("Access Secure Content"):
            try:
                decoded = jwt.decode(st.session_state.token, SECRET_KEY, algorithms=["HS256"])
                st.success(f"Access granted for user: {decoded['user']}")
                st.write("Secure Content: This is protected information accessible only with valid JWT.")
            except jwt.ExpiredSignatureError:
                st.error("Token has expired")
            except jwt.InvalidTokenError:
                st.error("Invalid token")

