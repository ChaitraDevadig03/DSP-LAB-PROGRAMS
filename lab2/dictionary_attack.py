import streamlit as st
import hashlib
import pandas as pd
import time
import re
from typing import List, Dict, Tuple, Optional
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Dictionary Attack Tool",
    page_icon="🔒",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2ca02c;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
    .danger-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

class PasswordAnalyzer:
    @staticmethod
    def check_password_strength(password: str) -> Tuple[str, int]:
        """Check password strength and return category and score"""
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 12:
            score += 3
            feedback.append("✓ Good length (12+ characters)")
        elif len(password) >= 8:
            score += 2
            feedback.append("✓ Moderate length (8-11 characters)")
        elif len(password) >= 4:
            score += 1
            feedback.append("✓ Minimum length (4-7 characters)")
        else:
            feedback.append("✗ Too short (less than 4 characters)")
        
        # Complexity checks
        if re.search(r'[A-Z]', password):
            score += 1
            feedback.append("✓ Contains uppercase letters")
        if re.search(r'[a-z]', password):
            score += 1
            feedback.append("✓ Contains lowercase letters")
        if re.search(r'[0-9]', password):
            score += 1
            feedback.append("✓ Contains numbers")
        if re.search(r'[^A-Za-z0-9]', password):
            score += 2
            feedback.append("✓ Contains special characters")
        
        # Common patterns to avoid
        common_patterns = ['123', 'abc', 'qwerty', 'password', 'admin', 'welcome']
        if any(pattern in password.lower() for pattern in common_patterns):
            score -= 1
            feedback.append("⚠ Contains common patterns")
        
        # Determine category
        if score >= 7:
            category = "Strong"
        elif score >= 4:
            category = "Medium"
        else:
            category = "Weak"
        
        return category, score, feedback

class DictionaryAttack:
    def __init__(self):
        self.common_hashes = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
    
    def hash_password(self, password: str, algorithm: str = 'sha256') -> str:
        """Hash a password using specified algorithm"""
        if algorithm not in self.common_hashes:
            algorithm = 'sha256'
        return self.common_hashes[algorithm](password.encode()).hexdigest()
    
    def dictionary_attack(self, target_hash: str, wordlist: List[str], 
                         algorithm: str = 'sha256', progress_callback=None) -> Optional[str]:
        """Perform dictionary attack on a hash"""
        if algorithm not in self.common_hashes:
            st.error(f"Unsupported algorithm: {algorithm}")
            return None
        
        total_words = len(wordlist)
        for i, word in enumerate(wordlist):
            word = word.strip()
            if not word:
                continue
                
            hashed_word = self.hash_password(word, algorithm)
            if hashed_word == target_hash:
                if progress_callback:
                    progress_callback(i + 1, total_words, f"Found: {word}")
                return word
            
            if progress_callback:
                progress_callback(i + 1, total_words, f"Testing: {word}")
        
        return None
    
    def brute_force_simulation(self, target: str, max_length: int = 6, 
                              charset: str = "abcdefghijklmnopqrstuvwxyz0123456789",
                              progress_callback=None) -> Optional[str]:
        """Simulate brute-force attack (for demonstration purposes)"""
        from itertools import product
        
        total_combinations = sum(len(charset) ** i for i in range(1, max_length + 1))
        tested = 0
        
        for length in range(1, max_length + 1):
            for combo in product(charset, repeat=length):
                tested += 1
                attempt = ''.join(combo)
                
                if progress_callback:
                    progress_callback(tested, total_combinations, f"Testing: {attempt}")
                
                if attempt == target:
                    if progress_callback:
                        progress_callback(tested, total_combinations, f"Found: {attempt}")
                    return attempt
                
                # Add small delay for realistic simulation
                time.sleep(0.001)
        
        return None

def main():
    st.markdown('<div class="main-header">🔒 Dictionary Attack & Password Analysis Tool</div>', 
                unsafe_allow_html=True)
    
    # Initialize classes
    analyzer = PasswordAnalyzer()
    attack = DictionaryAttack()
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs([
        "Password Analysis", 
        "Dictionary Attack", 
        "Brute Force Simulation",
        "Export Results"
    ])
    
    # Tab 1: Password Analysis
    with tab1:
        st.markdown('<div class="section-header">Password Strength Analysis</div>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            password_input = st.text_input("Enter password to analyze:", type="password")
            if password_input:
                category, score, feedback = analyzer.check_password_strength(password_input)
                
                st.write(f"**Password:** `{'*' * len(password_input)}`")
                st.write(f"**Strength:** {category}")
                st.write(f"**Score:** {score}/8")
                
                # Display feedback with appropriate styling
                for item in feedback:
                    if item.startswith("✓"):
                        st.success(item)
                    elif item.startswith("⚠"):
                        st.warning(item)
                    elif item.startswith("✗"):
                        st.error(item)
                    else:
                        st.info(item)
        
        with col2:
            st.info("""
            **Password Strength Criteria:**
            - Length: 4+ characters (minimum), 8+ recommended, 12+ strong
            - Uppercase letters: +1 point
            - Lowercase letters: +1 point  
            - Numbers: +1 point
            - Special characters: +2 points
            - Common patterns: -1 point
            
            **Categories:**
            - Weak: 0-3 points
            - Medium: 4-6 points  
            - Strong: 7-8 points
            """)
    
    # Tab 2: Dictionary Attack
    with tab2:
        st.markdown('<div class="section-header">Dictionary Attack</div>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            attack_type = st.radio("Attack type:", ["Hash Attack", "Plaintext Attack"])
            
            if attack_type == "Hash Attack":
                target_hash = st.text_input("Enter target hash:")
                hash_algorithm = st.selectbox("Hash algorithm:", 
                                            list(attack.common_hashes.keys()))
            else:
                target_plaintext = st.text_input("Enter target password:", type="password")
            
            uploaded_file = st.file_uploader("Upload dictionary file:", type=['txt'])
            
            if uploaded_file:
                wordlist = uploaded_file.read().decode('utf-8').splitlines()
                st.info(f"Loaded {len(wordlist)} words from dictionary")
        
        with col2:
            if st.button("Start Dictionary Attack", type="primary"):
                if not uploaded_file:
                    st.error("Please upload a dictionary file first!")
                    return
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total, message):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"{message} | Progress: {current}/{total} ({progress:.1%})")
                
                if attack_type == "Hash Attack":
                    if not target_hash:
                        st.error("Please enter a target hash!")
                        return
                    
                    result = attack.dictionary_attack(
                        target_hash, wordlist, hash_algorithm, update_progress
                    )
                    
                    if result:
                        st.success(f"✅ Password found: **{result}**")
                        st.session_state.found_password = result
                        st.session_state.password_category, _, _ = analyzer.check_password_strength(result)
                    else:
                        st.error("❌ Password not found in dictionary")
                
                else:
                    if not target_plaintext:
                        st.error("Please enter a target password!")
                        return
                    
                    # For plaintext attack, we'll hash the target first
                    target_hash = attack.hash_password(target_plaintext)
                    result = attack.dictionary_attack(
                        target_hash, wordlist, 'sha256', update_progress
                    )
                    
                    if result:
                        st.success(f"✅ Password found in dictionary: **{result}**")
                        st.session_state.found_password = result
                        st.session_state.password_category, _, _ = analyzer.check_password_strength(result)
                    else:
                        st.error("❌ Password not found in dictionary")
    
    # Tab 3: Brute Force Simulation
    with tab3:
        st.markdown('<div class="section-header">Brute Force Simulation</div>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_password = st.text_input("Target password for simulation:", type="password")
            max_length = st.slider("Maximum length to test:", 1, 8, 4)
            charset = st.text_input("Character set:", "abcdefghijklmnopqrstuvwxyz0123456789")
        
        with col2:
            if st.button("Start Brute Force Simulation", type="primary"):
                if not target_password:
                    st.error("Please enter a target password!")
                    return
                
                if len(target_password) > max_length:
                    st.warning(f"Target password length ({len(target_password)}) exceeds maximum test length ({max_length})")
                    return
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                time_estimate = st.empty()
                
                def update_progress(current, total, message):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"{message} | Progress: {current}/{total} ({progress:.1%})")
                    if progress > 0:
                        elapsed = time.time() - start_time
                        estimated_total = elapsed / progress
                        remaining = estimated_total - elapsed
                        time_estimate.text(f"Estimated time remaining: {remaining:.1f} seconds")
                
                start_time = time.time()
                result = attack.brute_force_simulation(
                    target_password, max_length, charset, update_progress
                )
                
                if result:
                    st.success(f"✅ Password cracked: **{result}**")
                    st.session_state.found_password = result
                    st.session_state.password_category, _, _ = analyzer.check_password_strength(result)
                else:
                    st.error("❌ Password not found (simulation incomplete)")
    
    # Tab 4: Export Results
    with tab4:
        st.markdown('<div class="section-header">Export Analysis Results</div>', 
                   unsafe_allow_html=True)
        
        if 'found_password' in st.session_state:
            password = st.session_state.found_password
            category = st.session_state.get('password_category', 'Unknown')
            
            st.write(f"**Password to export:** {password}")
            st.write(f"**Category:** {category}")
            
            # Create analysis data
            analysis_data = {
                'password': [password],
                'category': [category],
                'length': [len(password)],
                'has_uppercase': [bool(re.search(r'[A-Z]', password))],
                'has_lowercase': [bool(re.search(r'[a-z]', password))],
                'has_numbers': [bool(re.search(r'[0-9]', password))],
                'has_special': [bool(re.search(r'[^A-Za-z0-9]', password))]
            }
            
            df = pd.DataFrame(analysis_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV export
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="password_analysis.csv",
                    mime="text/csv"
                )
            
            with col2:
                # TXT export
                txt_content = f"""Password Analysis Report
================================
Password: {password}
Category: {category}
Length: {len(password)}
Contains uppercase: {analysis_data['has_uppercase'][0]}
Contains lowercase: {analysis_data['has_lowercase'][0]}
Contains numbers: {analysis_data['has_numbers'][0]}
Contains special chars: {analysis_data['has_special'][0]}

Generated on: {pd.Timestamp.now()}
"""
                st.download_button(
                    label="Download TXT",
                    data=txt_content,
                    file_name="password_analysis.txt",
                    mime="text/plain"
                )
        else:
            st.info("No passwords to export yet. Run an attack or analysis first.")

if __name__ == "__main__":
    main()
