# 🔒 Secure Real-Time Messaging Application

A secure real-time messaging application that provides:
- **Transport Layer Security (TLS)** for secure client-server communication
- **End-to-End Encryption (E2EE)** ensuring only sender and recipient can read messages
- **Real-time messaging** using WebSocket protocol
- **Streamlit-based** user interface

## 🚀 Features

- **TLS Encryption**: Secure WebSocket connections (wss://)
- **End-to-End Encryption**: Messages encrypted with RSA-2048
- **Real-time Communication**: Instant message delivery
- **Secure Key Exchange**: Public key exchange for E2EE
- **Message Relay Server**: Server acts only as message relay, cannot decrypt messages

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies:**
```bash
pip install streamlit websockets cryptography pyopenssl aiohttp
```

## 🔐 SSL Certificate Setup (Required for TLS)

Generate self-signed SSL certificates for development:

```bash
# Generate private key and certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Answer the prompts (you can use defaults for development)
```

## 🚀 Running the Application

### Step 1: Start the WebSocket Server

**Terminal 1 - Start the secure messaging server:**
```bash
python websocket_server.py
```

The server will start on:
- Secure: `wss://localhost:8765` (if certificates are available)
- Insecure: `ws://localhost:8765` (if no certificates)

### Step 2: Start the Streamlit Client

**Terminal 2 - Start the messaging client:**
```bash
streamlit run messaging_app.py
```

The application will open in your browser at `http://localhost:8501`

## 🎯 Usage

1. **Open multiple browser tabs/windows** to simulate multiple devices
2. **Connect to the server** using the sidebar settings
3. **Wait for key exchange** - the application will automatically exchange public keys
4. **Start messaging** - type messages and click send
5. **Messages are encrypted** end-to-end and relayed through the server

## 🔒 Security Features

### TLS Encryption
- Secure WebSocket connections (wss://)
- SSL/TLS encryption for all client-server communication
- Certificate-based server authentication

### End-to-End Encryption
- RSA-2048 asymmetric encryption
- Each client generates unique key pairs
- Public keys are exchanged through the server
- Only intended recipients can decrypt messages
- Server cannot decrypt message content

### Message Flow
1. Client A encrypts message with Client B's public key
2. Encrypted message sent to server via TLS
3. Server relays encrypted message to Client B
4. Client B decrypts message with their private key

## 📁 File Structure

```
├── messaging_app.py      # Streamlit client application
├── websocket_server.py   # Secure WebSocket server
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── cert.pem             # SSL certificate (generate)
└── key.pem              # SSL private key (generate)
```

## ⚠️ Important Notes

- **Development Use**: Self-signed certificates are for development only
- **Production**: Use proper CA-signed certificates for production
- **Multiple Clients**: Open multiple browser tabs to test multi-device communication
- **Firewall**: Ensure port 8765 is accessible if testing across networks

## 🐛 Troubleshooting

### Certificate Errors
If you see SSL errors, ensure:
- `cert.pem` and `key.pem` files exist in the project directory
- Certificates are properly generated

### Connection Issues
- Check that the WebSocket server is running
- Verify the server URL in the client matches the server configuration

### Dependency Issues
```bash
# Reinstall dependencies if needed
pip install -r requirements.txt
```

## 🔧 Customization

- **Port**: Change port 8765 in both server and client files
- **Host**: Update server address for network deployment
- **Encryption**: Modify encryption algorithms in `messaging_app.py`

## 📝 License

This project is for educational and development purposes. Ensure proper security measures for production use.
