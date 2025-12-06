import streamlit as st
import json
import os
import time
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoUtils:
    """Utility class for end-to-end encryption operations"""
    
    @staticmethod
    def generate_rsa_keypair():
        """Generate RSA public/private key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    @staticmethod
    def serialize_public_key(public_key):
        """Serialize public key to PEM format"""
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
    
    @staticmethod
    def deserialize_public_key(public_key_str):
        """Deserialize public key from PEM format"""
        return serialization.load_pem_public_key(
            public_key_str.encode('utf-8'),
            backend=default_backend()
        )
    
    @staticmethod
    def serialize_private_key(private_key, password=None):
        """Serialize private key to PEM format"""
        encryption_algorithm = serialization.NoEncryption()
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password.encode('utf-8'))
        
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        ).decode('utf-8')
    
    @staticmethod
    def deserialize_private_key(private_key_str, password=None):
        """Deserialize private key from PEM format"""
        return serialization.load_pem_private_key(
            private_key_str.encode('utf-8'),
            password=password.encode('utf-8') if password else None,
            backend=default_backend()
        )
    
    @staticmethod
    def generate_aes_key():
        """Generate random AES key (32 bytes for AES-256)"""
        return os.urandom(32)
    
    @staticmethod
    def encrypt_message(message, public_key):
        """Encrypt message using recipient's public key"""
        # Generate session key for AES encryption
        session_key = CryptoUtils.generate_aes_key()
        iv = os.urandom(16)  # Initialization vector
        
        # Encrypt message with AES
        cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad message to multiple of block size
        pad_length = 16 - (len(message) % 16)
        padded_message = message + bytes([pad_length] * pad_length)
        
        encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
        
        # Encrypt session key with RSA
        encrypted_session_key = public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            'encrypted_message': base64.b64encode(encrypted_message).decode('utf-8'),
            'encrypted_session_key': base64.b64encode(encrypted_session_key).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8')
        }
    
    @staticmethod
    def decrypt_message(encrypted_data, private_key):
        """Decrypt message using private key"""
        try:
            # Decode base64 values
            encrypted_message = base64.b64decode(encrypted_data['encrypted_message'])
            encrypted_session_key = base64.b64decode(encrypted_data['encrypted_session_key'])
            iv = base64.b64decode(encrypted_data['iv'])
            
            # Decrypt session key with RSA
            session_key = private_key.decrypt(
                encrypted_session_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt message with AES
            cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_padded = decryptor.update(encrypted_message) + decryptor.finalize()
            
            # Remove padding
            pad_length = decrypted_padded[-1]
            decrypted_message = decrypted_padded[:-pad_length]
            
            return decrypted_message.decode('utf-8')
            
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def hash_password(password, salt=None):
        """Hash password using PBKDF2"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return base64.b64encode(key).decode('utf-8'), base64.b64encode(salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed_password, salt):
        """Verify password against stored hash"""
        salt_bytes = base64.b64decode(salt)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
            backend=default_backend()
        )
        
        try:
            key = kdf.derive(password.encode('utf-8'))
            stored_key = base64.b64decode(hashed_password)
            return key == stored_key
        except:
            return False

class UserManager:
    """Manages user authentication and key storage"""
    
    def __init__(self, storage_file='users.json'):
        self.storage_file = storage_file
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_users(self):
        """Save users to storage file"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def register_user(self, username, password):
        """Register a new user with encrypted key storage"""
        if username in self.users:
            raise ValueError("Username already exists")
        
        # Generate RSA key pair for the user
        private_key, public_key = CryptoUtils.generate_rsa_keypair()
        
        # Hash password and generate salt
        hashed_password, salt = CryptoUtils.hash_password(password)
        
        # Serialize keys
        public_key_str = CryptoUtils.serialize_public_key(public_key)
        private_key_str = CryptoUtils.serialize_private_key(private_key, password)
        
        # Store user data
        self.users[username] = {
            'hashed_password': hashed_password,
            'salt': salt,
            'public_key': public_key_str,
            'private_key': private_key_str,  # Encrypted with password
            'contacts': {}  # Store other users' public keys
        }
        
        self._save_users()
        return True
    
    def authenticate_user(self, username, password):
        """Authenticate user and load their private key"""
        if username not in self.users:
            return False, None
        
        user_data = self.users[username]
        
        # Verify password
        if not CryptoUtils.verify_password(password, user_data['hashed_password'], user_data['salt']):
            return False, None
        
        try:
            # Load private key using password
            private_key = CryptoUtils.deserialize_private_key(user_data['private_key'], password)
            return True, private_key
        except Exception as e:
            print(f"Error loading private key: {e}")
            return False, None
    
    def get_user_public_key(self, username):
        """Get user's public key"""
        if username not in self.users:
            return None
        return self.users[username]['public_key']
    
    def add_contact(self, username, contact_username, contact_public_key):
        """Add a contact with their public key"""
        if username not in self.users:
            raise ValueError("User not found")
        
        # Verify the public key is valid
        try:
            CryptoUtils.deserialize_public_key(contact_public_key)
        except Exception as e:
            raise ValueError(f"Invalid public key: {e}")
        
        self.users[username]['contacts'][contact_username] = contact_public_key
        self._save_users()
    
    def get_contact_public_key(self, username, contact_username):
        """Get public key of a contact"""
        if (username not in self.users or 
            contact_username not in self.users[username]['contacts']):
            return None
        
        return self.users[username]['contacts'][contact_username]
    
    def get_contacts(self, username):
        """Get list of contacts for a user"""
        if username not in self.users:
            return []
        
        return list(self.users[username]['contacts'].keys())
    
    def user_exists(self, username):
        """Check if user exists"""
        return username in self.users
    
    def get_all_users(self):
        """Get list of all registered users"""
        return list(self.users.keys())
    
    def delete_user(self, username, password):
        """Delete a user account"""
        if username not in self.users:
            return False
        
        # Verify password first
        authenticated, _ = self.authenticate_user(username, password)
        if not authenticated:
            return False
        
        del self.users[username]
        self._save_users()
        return True

class MessageStore:
    """Stores and retrieves encrypted messages"""
    
    def __init__(self, storage_file='messages.json'):
        self.storage_file = storage_file
        self.messages = self._load_messages()
    
    def _load_messages(self):
        """Load messages from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_messages(self):
        """Save messages to storage file"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.messages, f, indent=2)
    
    def store_message(self, sender, recipient, encrypted_data):
        """Store an encrypted message"""
        message_id = f"{int(time.time() * 1000)}_{sender}_{recipient}"
        
        message = {
            'id': message_id,
            'sender': sender,
            'recipient': recipient,
            'encrypted_data': encrypted_data,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        # Initialize recipient's message list if it doesn't exist
        if recipient not in self.messages:
            self.messages[recipient] = []
        
        # Add message to recipient's inbox
        self.messages[recipient].append(message)
        self._save_messages()
        
        return message_id
    
    def get_messages(self, username, unread_only=False):
        """Get messages for a user"""
        if username not in self.messages:
            return []
        
        messages = self.messages[username]
        
        if unread_only:
            messages = [msg for msg in messages if not msg['read']]
        
        # Sort by timestamp (newest first)
        messages.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return messages
    
    def mark_as_read(self, username, message_id):
        """Mark a message as read"""
        if username not in self.messages:
            return False
        
        for message in self.messages[username]:
            if message['id'] == message_id:
                message['read'] = True
                self._save_messages()
                return True
        
        return False
    
    def get_conversation(self, user1, user2):
        """Get conversation between two users"""
        all_messages = []
        
        # Get messages where user1 sent to user2
        if user2 in self.messages:
            for msg in self.messages[user2]:
                if msg['sender'] == user1:
                    all_messages.append({
                        **msg,
                        'direction': 'sent'
                    })
        
        # Get messages where user2 sent to user1
        if user1 in self.messages:
            for msg in self.messages[user1]:
                if msg['sender'] == user2:
                    all_messages.append({
                        **msg,
                        'direction': 'received'
                    })
        
        # Sort by timestamp
        all_messages.sort(key=lambda x: x['timestamp'])
        
        return all_messages
    
    def delete_message(self, username, message_id):
        """Delete a message"""
        if username not in self.messages:
            return False
        
        for i, message in enumerate(self.messages[username]):
            if message['id'] == message_id:
                del self.messages[username][i]
                self._save_messages()
                return True
        
        return False
    
    def clear_conversation(self, user1, user2):
        """Clear conversation between two users"""
        deleted_count = 0
        
        # Delete messages from user1's inbox sent by user2
        if user1 in self.messages:
            self.messages[user1] = [
                msg for msg in self.messages[user1] 
                if msg['sender'] != user2
            ]
            deleted_count += len([msg for msg in self.messages[user1] if msg['sender'] == user2])
        
        # Delete messages from user2's inbox sent by user1
        if user2 in self.messages:
            self.messages[user2] = [
                msg for msg in self.messages[user2] 
                if msg['sender'] != user1
            ]
            deleted_count += len([msg for msg in self.messages[user2] if msg['sender'] == user1])
        
        self._save_messages()
        return deleted_count
    
    def get_message_count(self, username, unread_only=False):
        """Get count of messages for a user"""
        if username not in self.messages:
            return 0
        
        if unread_only:
            return sum(1 for msg in self.messages[username] if not msg['read'])
        
        return len(self.messages[username])
    
    def cleanup_old_messages(self, max_age_days=30):
        """Clean up messages older than specified days"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        deleted_count = 0
        
        for username in list(self.messages.keys()):
            original_count = len(self.messages[username])
            self.messages[username] = [
                msg for msg in self.messages[username]
                if datetime.fromisoformat(msg['timestamp']).timestamp() > cutoff_time
            ]
            deleted_count += original_count - len(self.messages[username])
        
        self._save_messages()
        return deleted_count

# Page configuration
st.set_page_config(
    page_title="Secure E2EE Messenger",
    page_icon="🔒",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.private_key = None
    st.session_state.user_manager = UserManager()
    st.session_state.message_store = MessageStore()

def login_user(username, password):
    """Authenticate user and load their private key"""
    authenticated, private_key = st.session_state.user_manager.authenticate_user(username, password)
    if authenticated:
        st.session_state.authenticated = True
        st.session_state.current_user = username
        st.session_state.private_key = private_key
        st.success(f"Welcome back, {username}!")
        return True
    else:
        st.error("Invalid username or password")
        return False

def register_user(username, password, confirm_password):
    """Register a new user"""
    if password != confirm_password:
        st.error("Passwords do not match")
        return False
    
    if len(password) < 8:
        st.error("Password must be at least 8 characters long")
        return False
    
    try:
        st.session_state.user_manager.register_user(username, password)
        st.success("Registration successful! Please log in.")
        return True
    except ValueError as e:
        st.error(str(e))
        return False

def send_message(recipient, message_text):
    """Send an encrypted message to recipient"""
    try:
        # Get recipient's public key
        recipient_public_key_str = st.session_state.user_manager.get_contact_public_key(
            st.session_state.current_user, recipient
        )
        
        if not recipient_public_key_str:
            st.error(f"{recipient} is not in your contacts or public key not found")
            return False
        
        # Deserialize recipient's public key
        recipient_public_key = CryptoUtils.deserialize_public_key(recipient_public_key_str)
        
        # Encrypt the message
        encrypted_data = CryptoUtils.encrypt_message(message_text.encode('utf-8'), recipient_public_key)
        
        # Store the encrypted message
        st.session_state.message_store.store_message(
            st.session_state.current_user, recipient, encrypted_data
        )
        
        st.success(f"Message sent to {recipient}!")
        return True
        
    except Exception as e:
        st.error(f"Failed to send message: {str(e)}")
        return False

def add_contact(contact_username, contact_public_key):
    """Add a new contact with their public key"""
    try:
        st.session_state.user_manager.add_contact(
            st.session_state.current_user, contact_username, contact_public_key
        )
        st.success(f"Added {contact_username} to contacts!")
        return True
    except ValueError as e:
        st.error(str(e))
        return False

def main():
    """Main application function"""
    st.title("🔒 Secure End-to-End Encrypted Messenger")
    
    # Authentication section
    if not st.session_state.authenticated:
        st.header("Authentication")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    login_user(username, password)
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Register")
                
                if submitted:
                    if register_user(new_username, new_password, confirm_password):
                        # Auto-switch to login tab after successful registration
                        st.rerun()
        
        # Show public key exchange instructions
        st.info("""
        **How it works:**
        - Each user generates their own RSA key pair
        - Messages are encrypted with AES and the session key is encrypted with RSA
        - Only the intended recipient can decrypt messages
        - Even the server cannot read your messages!
        """)
        
        return
    
    # Main application after authentication
    st.sidebar.title(f"Welcome, {st.session_state.current_user}!")
    
    # Navigation
    app_section = st.sidebar.radio(
        "Navigation",
        ["Messaging", "Contacts", "My Public Key", "Settings"]
    )
    
    # Messaging section
    if app_section == "Messaging":
        st.header("💬 Secure Messaging")
        
        # Get user's contacts
        contacts = st.session_state.user_manager.get_contacts(st.session_state.current_user)
        
        if not contacts:
            st.info("Add contacts first to start messaging!")
            return
        
        # Select contact to message
        selected_contact = st.selectbox("Select contact to message", contacts)
        
        if selected_contact:
            # Show conversation
            conversation = st.session_state.message_store.get_conversation(
                st.session_state.current_user, selected_contact
            )
            
            # Display messages
            st.subheader(f"Conversation with {selected_contact}")
            
            for msg in conversation:
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    if msg['direction'] == 'sent':
                        st.write("**You:**")
                    else:
                        st.write(f"**{selected_contact}:**")
                
                with col2:
                    if msg['direction'] == 'received' and not msg['read']:
                        try:
                            # Decrypt received message
                            decrypted_message = CryptoUtils.decrypt_message(
                                msg['encrypted_data'], st.session_state.private_key
                            )
                            st.success(decrypted_message)
                            st.session_state.message_store.mark_as_read(
                                st.session_state.current_user, msg['id']
                            )
                        except Exception as e:
                            st.error(f"Failed to decrypt message: {str(e)}")
                    elif msg['direction'] == 'sent':
                        st.info("🔒 Encrypted message sent")
                    else:
                        st.info("🔒 Encrypted message (already read)")
            
            # Send message form
            with st.form("message_form"):
                message_text = st.text_area("Type your message", height=100)
                send_button = st.form_submit_button("Send Encrypted Message")
                
                if send_button and message_text.strip():
                    if send_message(selected_contact, message_text.strip()):
                        st.rerun()
    
    # Contacts section
    elif app_section == "Contacts":
        st.header("👥 Contacts Management")
        
        # Show current contacts
        contacts = st.session_state.user_manager.get_contacts(st.session_state.current_user)
        
        if contacts:
            st.subheader("Your Contacts")
            for contact in contacts:
                st.write(f"- {contact}")
        else:
            st.info("No contacts yet. Add some below!")
        
        # Add new contact
        st.subheader("Add New Contact")
        with st.form("add_contact_form"):
            contact_username = st.text_input("Contact Username")
            contact_public_key = st.text_area("Contact Public Key (PEM format)", height=150)
            add_button = st.form_submit_button("Add Contact")
            
            if add_button:
                if add_contact(contact_username, contact_public_key):
                    st.rerun()
    
    # Public key section
    elif app_section == "My Public Key":
        st.header("🔑 My Public Key")
        
        # Display user's public key
        public_key = st.session_state.user_manager.get_user_public_key(st.session_state.current_user)
        
        st.success("Your public key (share this with others to receive messages):")
        st.code(public_key, language="text")
        
        st.info("""
        **Instructions:**
        1. Share this public key with people you want to communicate with
        2. They need to add you as a contact using this key
        3. You'll be able to send encrypted messages to each other
        """)
    
    # Settings section
    elif app_section == "Settings":
        st.header("⚙️ Settings")
        
        # Logout button
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.private_key = None
            st.rerun()
        
        # Message statistics
        total_messages = st.session_state.message_store.get_message_count(st.session_state.current_user)
        unread_messages = st.session_state.message_store.get_message_count(st.session_state.current_user, unread_only=True)
        
        st.write(f"**Total messages:** {total_messages}")
        st.write(f"**Unread messages:** {unread_messages}")
        
        # Cleanup old messages
        if st.button("Cleanup messages older than 30 days"):
            deleted = st.session_state.message_store.cleanup_old_messages(30)
            st.success(f"Cleaned up {deleted} old messages")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Security Features:**
    - End-to-End Encryption (E2EE)
    - RSA 2048-bit key exchange
    - AES-256 message encryption
    - Password-protected private keys
    - Server cannot read your messages
    """)

if __name__ == "__main__":
    main()
