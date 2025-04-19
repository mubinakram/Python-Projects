import streamlit as st
from cryptography.fernet import Fernet
import hashlib
import base64


if "stored_data" not in st.session_state:
    st.session_state["stored_data"] = {}

login_credentials = {"admin": "admin123"}  


if "attempts" not in st.session_state:
    st.session_state["attempts"] = 0


def generate_key(passkey: str) -> bytes:
    hash_obj = hashlib.sha256(passkey.encode())
    key = base64.urlsafe_b64encode(hash_obj.digest())
    return key

def encrypt_data(data: str, passkey: str) -> str:
    key = generate_key(passkey)
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str, passkey: str) -> str:
    try:
        key = generate_key(passkey)
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data.encode()).decode()
    except:
        return None


def home():
    st.title("🛡️ Secure Data Encryption System")
    choice = st.radio("Choose an action:", ["Insert Data", "Retrieve Data"])
    if choice == "Insert Data":
        insert_data()
    elif choice == "Retrieve Data":
        if st.session_state["attempts"] >= 3:
            st.warning("Too many failed attempts. Please login again.")
            login()
        else:
            retrieve_data()

def insert_data():
    st.header("🔐 Insert Data")
    username = st.text_input("Username")
    data = st.text_area("Enter your data")
    passkey = st.text_input("Passkey", type="password")

    if st.button("Store Data"):
        if username and data and passkey:
            encrypted_text = encrypt_data(data, passkey)
            st.session_state["stored_data"][username] = {
                "encrypted_text": encrypted_text,
                "passkey": hashlib.sha256(passkey.encode()).hexdigest()
            }
            st.success("Data encrypted and stored successfully!")
        else:
            st.error("All fields are required.")

def retrieve_data():
    st.header("🔓 Retrieve Data")
    username = st.text_input("Username")
    passkey = st.text_input("Passkey", type="password")

    if st.button("Decrypt Data"):
        if username in st.session_state["stored_data"]:
            expected_hash = st.session_state["stored_data"][username]["passkey"]
            if hashlib.sha256(passkey.encode()).hexdigest() == expected_hash:
                decrypted_text = decrypt_data(st.session_state["stored_data"][username]["encrypted_text"], passkey)
                if decrypted_text:
                    st.success("Data Decrypted:")
                    st.code(decrypted_text)
                    st.session_state["attempts"] = 0  # reset on success
                else:
                    st.error("Decryption failed.")
                    st.session_state["attempts"] += 1
            else:
                st.error("Incorrect passkey.")
                st.session_state["attempts"] += 1
        else:
            st.error("Username not found.")

        st.info(f"Failed Attempts: {st.session_state['attempts']}/3")

def login():
    st.header("🔐 Reauthorization Required")
    username = st.text_input("Login Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in login_credentials and login_credentials[username] == password:
            st.success("Login successful. You can now retry.")
            st.session_state["attempts"] = 0
        else:
            st.error("Login failed. Try again.")


home()
