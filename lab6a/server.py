import socket
import ssl
import threading

HOST = 'localhost'
PORT = 12345

clients = []
lock = threading.Lock()

def handle_client(conn, addr):
    """Handles a single client connection."""
    print(f"Connected by {addr}")
    with lock:
        clients.append(conn)
    
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            # Relay message to the other client(s)
            with lock:
                for client in clients:
                    if client != conn:
                        try:
                            client.sendall(data)
                        except socket.error:
                            # Handle broken pipe if a client disconnects abruptly
                            clients.remove(client)
    finally:
        with lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"Disconnected from {addr}")

def main():
    """Main server function."""
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen(5)
        print(f"Server listening on {HOST}:{PORT}")

        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                conn, addr = ssock.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()

if __name__ == "__main__":
    main()
