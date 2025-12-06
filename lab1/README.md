# CIA Triad Simulation

A comprehensive Python-based simulation demonstrating the three fundamental principles of information security: Confidentiality, Integrity, and Availability (CIA Triad).

## 🎯 What is the CIA Triad?

The CIA Triad represents the three core components of information security:

- **Confidentiality**: Protecting information from unauthorized access
- **Integrity**: Ensuring information hasn't been tampered with or altered
- **Availability**: Ensuring information and systems are accessible when needed

## 📋 Features

### 🔒 Confidentiality Demonstration
- Data encryption using Fernet symmetric encryption
- Secure key management
- Unauthorized access prevention
- Secure data transmission simulation

### 🔍 Integrity Demonstration
- Cryptographic hashing (SHA-256)
- Data tampering detection
- Digital signature verification
- Checksum validation

### ⚡ Availability Demonstration
- DDoS attack simulation
- Redundancy and failover mechanisms
- Service availability monitoring
- Disaster recovery simulation

## 🚀 Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## 💻 Usage

### Command Line Simulation
Run the main simulation:

```bash
python cia_triad_simulation.py
```

### Interactive Console Demo
Run the interactive version:

```bash
python interactive_cia_demo.py
```

### Web-based Streamlit App
Run the Streamlit web application:

```bash
streamlit run streamlit_cia_demo.py
```

## 📊 Simulation Output

The programs will demonstrate:

1. **Confidentiality**: Encrypts sensitive data and shows how unauthorized access is prevented
2. **Integrity**: Uses hashing to detect data tampering during transmission
3. **Availability**: Simulates DDoS attacks and shows redundancy mechanisms

## 🛠️ Technical Implementation

### Encryption
- Uses Fernet symmetric encryption from the cryptography library
- 128-bit AES encryption in CBC mode
- HMAC authentication

### Hashing
- SHA-256 for integrity verification
- Cryptographic hash functions for tamper detection

### Web Interface
- Streamlit for interactive web-based demonstrations
- Real-time encryption/decryption
- Interactive integrity verification

### Security Features
- Secure random number generation
- Proper key management
- Error handling for security failures

## 🎓 Educational Value

This simulation helps understand:
- How encryption protects data confidentiality
- How hashing ensures data integrity
- Why availability is crucial for system reliability
- Real-world security scenarios and mitigations
- Interactive web-based security demonstrations

## 🔧 Customization

You can modify the simulation by:
- Changing encryption algorithms
- Adjusting security parameters
- Adding new attack scenarios
- Implementing additional security measures
- Extending the Streamlit interface

## 📝 License

This project is for educational purposes. Feel free to use and modify as needed.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## ⚠️ Disclaimer

This is an educational simulation. For production systems, always use professionally vetted security libraries and follow security best practices.
