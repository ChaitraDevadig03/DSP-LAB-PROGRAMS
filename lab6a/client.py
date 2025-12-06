import socket
import ssl
import threading
from lab3_crypto import encrypt_message, decrypt_message, generate_key

HOST = 'localhost'
PORT = 12345

# In a real application, this key would be established via a secure key exchange protocol
# For this simulation, we'll use a pre-shared key for simplicity.
SHARED_KEY = b'pre-shared-key-must-be-32-bytes'

def receive_messages(sock, key):
    """Receives and decrypts messages from the server."""
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            decrypted_message = decrypt_message(key, data)
            print(f"\nReceived: {decrypted_message}\n> ", end="")
    except (ssl.SSLError, ConnectionResetError):
        print("Connection closed.")
    finally:
        sock.close()

def send_messages(sock, key):
    """Encrypts and sends messages from user input."""
    try:
        while True:
            message = input("> ")
            encrypted_message = encrypt_message(key, message)
            sock.sendall(encrypted_message)
    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
    finally:
        sock.close()

def main():
    """Main client function."""
    # For a self-signed certificate, we need to trust it explicitly.
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile="cert.pem")
    context.check_hostname = False # Not recommended for production

    with socket.create_connection((HOST, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            print("Connected to the server.")
            
            # For this demo, we'll use a fixed key. 
            # A real E2EE system would use a key derived from a key exchange.
            # We'll generate a key from our pre-shared secret.
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.backends import default_backend
            import base64

            salt = b'salt_' # In a real app, this would also be exchanged
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(SHARED_KEY))

            print("End-to-end encryption key established.")

            receive_thread = threading.Thread(target=receive_messages, args=(ssock, key))
            receive_thread.daemon = True
            receive_thread.start()

            send_thread = threading.Thread(target=send_messages, args=(ssock, key))
            send_thread.start()
            send_thread.join()

if __name__ == "__main__":
    main()
