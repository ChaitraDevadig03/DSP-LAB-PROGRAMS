import streamlit as st
import hashlib
import base64
import re

# --- HASHING FUNCTIONS ---
def hash_text(text, algorithm="sha256"):
    if algorithm == "sha256":
        return hashlib.sha256(text.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()

def hash_file(file, algorithm="sha256"):
    file_data = file.read()
    if algorithm == "sha256":
        return hashlib.sha256(file_data).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(file_data).hexdigest()

# --- SIMPLE OBFUSCATION ---
def obfuscate_code(code):
    # Encode function body in base64 for hiding
    encoded = base64.b64encode(code.encode()).decode()
    obfuscated = f"""
import base64
exec(base64.b64decode("{encoded}").decode())
"""
    return obfuscated

# --- STREAMLIT APP ---
st.title("🔐 Hash Functions & Code Obfuscation Tool")

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Choose an option", ["Hash Generator", "Code Obfuscator"])

# HASH GENERATOR
if choice == "Hash Generator":
    st.header("Generate Hash Values (MD5 / SHA-256)")

    input_type = st.radio("Choose input type", ["Text", "File"])

    if input_type == "Text":
        user_input = st.text_area("Enter text to hash")
        if st.button("Generate Hash"):
            if user_input:
                st.write("**MD5 Hash:**", hash_text(user_input, "md5"))
                st.write("**SHA-256 Hash:**", hash_text(user_input, "sha256"))
            else:
                st.warning("Please enter some text.")

    else:  # File Input
        uploaded_file = st.file_uploader("Upload a file")
        if uploaded_file is not None:
            if st.button("Generate File Hash"):
                st.write("**MD5 Hash:**", hash_file(uploaded_file, "md5"))
                uploaded_file.seek(0)  # reset pointer for second read
                st.write("**SHA-256 Hash:**", hash_file(uploaded_file, "sha256"))

# CODE OBFUSCATOR
elif choice == "Code Obfuscator":
    st.header("Python Code Obfuscator")

    user_code = st.text_area("Paste your Python function code here")

    if st.button("Obfuscate Code"):
        if user_code.strip():
            st.subheader("🔎 Original Code")
            st.code(user_code, language="python")

            obfuscated_code = obfuscate_code(user_code)
            st.subheader("🕵️ Obfuscated Code")
            st.code(obfuscated_code, language="python")
        else:
            st.warning("Please paste some Python code.")
