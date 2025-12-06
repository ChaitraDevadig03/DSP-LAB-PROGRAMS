"""
Streamlit CIA Triad Demonstration
Comprehensive web app merging all CIA triad functionalities
Combines features from cia_triad_simulation.py and interactive_cia_demo.py
"""

import streamlit as st
import hashlib
import secrets
from cryptography.fernet import Fernet
import time
import random
import threading

# Set page configuration
st.set_page_config(
    page_title="CIA Triad Demo",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

class CIATriadDemo:
    """Comprehensive CIA Triad demonstration class"""
    
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.data_store = {}
        self.availability_status = True
        
        # Initialize session state
        if 'encryption_key' not in st.session_state:
            st.session_state.encryption_key = self.encryption_key
            st.session_state.cipher = self.cipher
            st.session_state.original_data = ""
            st.session_state.encrypted_data = b""
            st.session_state.original_hash = ""
            st.session_state.availability_status = True

    def demonstrate_confidentiality(self):
        """Confidentiality demonstration section"""
        st.header("🔒 Confidentiality - Data Protection")
        
        st.write("""
        Confidentiality ensures that sensitive information is accessed only by authorized individuals. 
        This is typically achieved through encryption, access controls, and authentication mechanisms.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Encryption Demo")
            sensitive_data = st.text_area(
                "Enter sensitive data to encrypt:",
                value="Credit card: 1234-5678-9012-3456, SSN: 123-45-6789",
                height=100
            )
            
            if st.button("🔐 Encrypt Data"):
                if sensitive_data:
                    encrypted = st.session_state.cipher.encrypt(sensitive_data.encode())
                    st.session_state.encrypted_data = encrypted
                    st.session_state.original_data = sensitive_data
                    
                    st.success("Data encrypted successfully!")
                    st.code(f"Encrypted: {encrypted}", language="text")
                else:
                    st.error("Please enter some data to encrypt")
        
        with col2:
            st.subheader("Decryption Demo")
            if st.session_state.encrypted_data:
                st.info("Encrypted data available for decryption")
                
                if st.button("🔓 Decrypt with Correct Key"):
                    decrypted = st.session_state.cipher.decrypt(st.session_state.encrypted_data).decode()
                    st.success("Decryption successful!")
                    st.code(f"Decrypted: {decrypted}", language="text")
                
                # Try with wrong key
                if st.button("❌ Try Wrong Key"):
                    wrong_key = Fernet.generate_key()
                    wrong_cipher = Fernet(wrong_key)
                    try:
                        wrong_cipher.decrypt(st.session_state.encrypted_data)
                        st.error("Security breach! Wrong key worked!")
                    except:
                        st.success("Security maintained! Wrong key rejected")
            else:
                st.warning("Encrypt some data first to see decryption")

    def demonstrate_integrity(self):
        """Integrity demonstration section"""
        st.header("🔍 Integrity - Data Authenticity")
        
        st.write("""
        Integrity ensures that data has not been altered or tampered with during storage or transmission. 
        This is typically achieved through cryptographic hashing and digital signatures.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Hash Generation")
            data_to_hash = st.text_area(
                "Enter data to hash:",
                value="This is important data that must not be tampered with",
                height=100,
                key="hash_input"
            )
            
            if st.button("📋 Generate Hash"):
                if data_to_hash:
                    hash_value = hashlib.sha256(data_to_hash.encode()).hexdigest()
                    st.session_state.original_hash = hash_value
                    st.session_state.original_data_hash = data_to_hash
                    
                    st.success("Hash generated successfully!")
                    st.code(f"SHA-256 Hash: {hash_value}", language="text")
                else:
                    st.error("Please enter some data to hash")
        
        with col2:
            st.subheader("Integrity Verification")
            if st.session_state.original_hash:
                st.info("Original hash is available for verification")
                
                verify_data = st.text_area(
                    "Enter data to verify:",
                    value=st.session_state.original_data_hash,
                    height=100,
                    key="verify_input"
                )
                
                if st.button("✅ Verify Integrity"):
                    current_hash = hashlib.sha256(verify_data.encode()).hexdigest()
                    
                    if current_hash == st.session_state.original_hash:
                        st.success("✅ Integrity verified! Data is authentic.")
                    else:
                        st.error("❌ Integrity compromised! Data has been tampered with.")
                    
                    st.write(f"Original hash: `{st.session_state.original_hash[:20]}...`")
                    st.write(f"Current hash: `{current_hash[:20]}...`")
            else:
                st.warning("Generate a hash first to verify integrity")

    def demonstrate_availability(self):
        """Enhanced Availability demonstration section"""
        st.header("⚡ Availability - System Reliability & Redundancy")
        
        st.write("""
        Availability ensures that systems and data are accessible when needed by authorized users. 
        This involves redundancy, failover mechanisms, load balancing, backup systems, and protection against denial-of-service attacks.
        """)
        
        # Initialize session state for enhanced availability features
        if 'server_health' not in st.session_state:
            st.session_state.server_health = {
                'Primary': {'status': 'online', 'load': 30, 'uptime': '99.95%'},
                'Backup 1': {'status': 'online', 'load': 15, 'uptime': '99.98%'},
                'Backup 2': {'status': 'online', 'load': 10, 'uptime': '99.99%'},
                'Backup 3': {'status': 'online', 'load': 5, 'uptime': '99.99%'}
            }
        
        if 'sla_status' not in st.session_state:
            st.session_state.sla_status = {
                'uptime': '99.95%',
                'response_time': '150ms',
                'throughput': '1.2 Gbps',
                'compliance': 'Meeting SLA'
            }
        
        if 'backup_status' not in st.session_state:
            st.session_state.backup_status = {
                'hot_backup': 'Active',
                'warm_backup': 'Standby', 
                'cold_backup': 'Ready',
                'last_backup': '5 minutes ago'
            }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Real-time System Monitoring")
            
            # System status with enhanced metrics
            status_col1, status_col2 = st.columns(2)
            
            with status_col1:
                if st.session_state.availability_status:
                    st.success("✅ System Operational")
                    st.metric("Uptime", "99.95%", "0.02%")
                    st.metric("Response Time", "150ms", "-5ms")
                else:
                    st.error("❌ System Degraded")
                    st.metric("Uptime", "85.2%", "-14.75%")
                    st.metric("Response Time", "1200ms", "+1050ms")
            
            with status_col2:
                st.metric("Active Users", "1,245", "12")
                st.metric("Throughput", "1.2 Gbps", "0.1 Gbps")
                st.metric("Error Rate", "0.05%", "0.01%")
            
            # Server health dashboard
            st.subheader("🖥️ Server Health Status")
            for server, stats in st.session_state.server_health.items():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    status_icon = "✅" if stats['status'] == 'online' else "❌"
                    st.write(f"{status_icon} **{server}**")
                with col_b:
                    st.write(f"Load: {stats['load']}%")
                with col_c:
                    st.write(f"Uptime: {stats['uptime']}")
            
            # SLA Compliance
            st.subheader("📋 SLA Compliance")
            sla_col1, sla_col2 = st.columns(2)
            with sla_col1:
                st.metric("Uptime SLA", st.session_state.sla_status['uptime'])
                st.metric("Response SLA", st.session_state.sla_status['response_time'])
            with sla_col2:
                st.metric("Throughput", st.session_state.sla_status['throughput'])
                status_color = "🟢" if st.session_state.sla_status['compliance'] == 'Meeting SLA' else "🔴"
                st.write(f"{status_color} {st.session_state.sla_status['compliance']}")
        
        with col2:
            st.subheader("🛡️ Attack Simulation & Recovery")
            
            attack_type = st.selectbox(
                "Select Attack Type:",
                ["DDoS Flood", "Resource Exhaustion", "DNS Amplification", "Slowloris"]
            )
            
            if st.button("🎯 Launch Attack Simulation", type="primary"):
                st.session_state.availability_status = False
                
                # Update metrics for attack scenario
                st.session_state.sla_status.update({
                    'uptime': '85.2%',
                    'response_time': '1200ms', 
                    'throughput': '0.3 Gbps',
                    'compliance': 'SLA Violation'
                })
                
                # Simulate server impact
                for server in st.session_state.server_health:
                    if random.random() < 0.7:  # 70% chance server is affected
                        st.session_state.server_health[server]['status'] = 'degraded'
                        st.session_state.server_health[server]['load'] = min(95, st.session_state.server_health[server]['load'] + random.randint(40, 70))
                
                st.error(f"❌ Under {attack_type} attack! Service degraded...")
                
                # Enhanced recovery simulation
                def recover():
                    time.sleep(4)  # Longer recovery for realism
                    st.session_state.availability_status = True
                    
                    # Restore normal metrics
                    st.session_state.sla_status.update({
                        'uptime': '99.95%',
                        'response_time': '150ms',
                        'throughput': '1.2 Gbps',
                        'compliance': 'Meeting SLA'
                    })
                    
                    # Restore server health
                    for server in st.session_state.server_health:
                        st.session_state.server_health[server]['status'] = 'online'
                        st.session_state.server_health[server]['load'] = random.randint(5, 35)
                
                thread = threading.Thread(target=recover)
                thread.daemon = True
                thread.start()
            
            st.subheader("🔄 Redundancy & Failover")
            
            failover_col1, failover_col2 = st.columns(2)
            
            with failover_col1:
                if st.button("🔄 Simulate Server Failure"):
                    available_servers = [s for s, stats in st.session_state.server_health.items() 
                                       if stats['status'] == 'online']
                    if available_servers:
                        failed_server = random.choice(available_servers)
                        st.session_state.server_health[failed_server]['status'] = 'failed'
                        st.session_state.server_health[failed_server]['load'] = 0
                        
                        st.warning(f"⚠️ {failed_server} server failed!")
                        st.success("✅ Automatic failover initiated!")
                        
                        # Simulate load redistribution
                        for server in st.session_state.server_health:
                            if server != failed_server and st.session_state.server_health[server]['status'] == 'online':
                                st.session_state.server_health[server]['load'] = min(
                                    80, st.session_state.server_health[server]['load'] + 15
                                )
            
            with failover_col2:
                if st.button("🔄 Manual Failover Test"):
                    st.info("🔧 Testing failover mechanisms...")
                    time.sleep(1)
                    st.success("✅ Failover test completed successfully!")
                    st.session_state.sla_status['uptime'] = '99.97%'
            
            st.subheader("💾 Backup Systems")
            
            backup_col1, backup_col2, backup_col3 = st.columns(3)
            
            with backup_col1:
                st.write("**Hot Backup**")
                st.success(st.session_state.backup_status['hot_backup'])
            
            with backup_col2:
                st.write("**Warm Backup**")
                st.info(st.session_state.backup_status['warm_backup'])
            
            with backup_col3:
                st.write("**Cold Backup**")
                st.warning(st.session_state.backup_status['cold_backup'])
            
            st.write(f"**Last Backup:** {st.session_state.backup_status['last_backup']}")
            
            if st.button("🔄 Run Backup Now"):
                st.info("📦 Starting backup procedure...")
                time.sleep(2)
                st.session_state.backup_status['last_backup'] = 'Just now'
                st.success("✅ Backup completed successfully!")
                
            st.subheader("⚖️ Load Balancing")
            load_distribution = st.slider("Traffic Distribution (%)", 0, 100, 60)
            st.write(f"**Load Distribution:** {load_distribution}% primary, {100-load_distribution}% backups")
            st.progress(load_distribution/100)
            
            if st.button("🔄 Optimize Load Balance"):
                optimal_load = random.randint(40, 60)
                st.success(f"✅ Load optimized to {optimal_load}% distribution")

    def password_security(self):
        """Password security demonstration"""
        st.header("🔐 Password Security")
        
        st.write("""
        Strong authentication is crucial for maintaining confidentiality. Weak passwords are a common security vulnerability.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Weak Passwords (Avoid These)")
            weak_passwords = [
                "password123", "123456", "qwerty", 
                "letmein", "admin", "welcome"
            ]
            
            for pwd in weak_passwords:
                st.error(f"❌ {pwd}")
        
        with col2:
            st.subheader("Strong Password Generator")
            length = st.slider("Password length", 8, 32, 16)
            
            if st.button("🎲 Generate Strong Password"):
                strong_password = self.generate_secure_password(length)
                
                st.success("Strong password generated!")
                st.code(strong_password, language="text")
                
                # Password strength analysis
                st.info(f"**Strength Analysis:**")
                st.write(f"- Length: {length} characters")
                st.write("- Contains uppercase, lowercase, numbers, and symbols")
                st.write("- Randomly generated (high entropy)")

    def generate_secure_password(self, length=16):
        """Generate a secure random password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    """Main application"""
    demo = CIATriadDemo()
    
    st.title("🔒 CIA Triad Demonstration")
    st.write("Interactive exploration of Information Security Fundamentals")
    
    # Create sidebar navigation
    st.sidebar.title("Navigation")
    section = st.sidebar.radio(
        "Choose a section:",
        [
            "Overview", 
            "Confidentiality", 
            "Integrity", 
            "Availability", 
            "Password Security"
        ]
    )
    
    if section == "Overview":
        st.header("🎯 CIA Triad Overview")
        st.write("""
        The CIA Triad represents the three fundamental principles of information security:
        
        **🔒 Confidentiality** - Protecting information from unauthorized access
        - Encryption
        - Access controls  
        - Authentication
        - Data classification
        
        **🔍 Integrity** - Ensuring information hasn't been tampered with
        - Cryptographic hashing
        - Digital signatures
        - Checksums
        - Version control
        
        **⚡ Availability** - Ensuring information is accessible when needed
        - Redundancy
        - Failover systems
        - DDoS protection
        - Backup and recovery
        """)
        
        st.info("""
        **Additional Features:**
        - 🔐 Password security best practices
        """)
        
    elif section == "Confidentiality":
        demo.demonstrate_confidentiality()
        
    elif section == "Integrity":
        demo.demonstrate_integrity()
        
    elif section == "Availability":
        demo.demonstrate_availability()
        
    elif section == "Password Security":
        demo.password_security()
        
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Educational Tool**  
    This demonstration is for educational purposes only.  
    Always use professionally vetted security solutions in production environments.
    
    **Merged Features From:**
    - Original Streamlit Demo
    - CIA Triad Simulation
    - Interactive CIA Demo
    """)

if __name__ == "__main__":
    main()
