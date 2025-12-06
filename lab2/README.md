# Dictionary Attack & Password Analysis Tool

A comprehensive Streamlit-based application for password security analysis, dictionary attacks, and brute-force simulations.

## Features

### ✅ Password Analysis
- **Strength Assessment**: Classifies passwords as Weak, Medium, or Strong
- **Detailed Feedback**: Provides specific feedback on password weaknesses
- **Scoring System**: 8-point scale based on complexity criteria

### ✅ Dictionary Attack
- **Hash Attack**: Crack hashed passwords using dictionary wordlists
- **Plaintext Attack**: Check if plaintext passwords exist in dictionaries
- **Multiple Algorithms**: Supports MD5, SHA1, SHA256, SHA512
- **Real-time Progress**: Live progress bar during attacks

### ✅ Brute Force Simulation
- **Configurable Parameters**: Set maximum length and character sets
- **Realistic Simulation**: Includes timing estimates
- **Educational Purpose**: Demonstrates brute-force attack principles

### ✅ Export Functionality
- **CSV Export**: Detailed analysis reports in CSV format
- **TXT Export**: Human-readable analysis reports
- **Categorized Results**: Export passwords by strength category

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run dictionary_attack_app.py
```

## Usage

### Password Analysis
1. Navigate to the "Password Analysis" tab
2. Enter a password to analyze
3. View strength category, score, and detailed feedback

### Dictionary Attack
1. Go to the "Dictionary Attack" tab
2. Choose attack type (Hash or Plaintext)
3. Upload a dictionary file (text file with one word per line)
4. Start the attack and monitor progress

### Brute Force Simulation
1. Visit the "Brute Force Simulation" tab  
2. Set target password and simulation parameters
3. Start simulation to see brute-force in action

### Export Results
1. After successful attacks, go to "Export Results"
2. Download analysis reports in CSV or TXT format

## Sample Dictionary

The `sample_dictionary.txt` file contains common passwords for testing purposes. For real-world usage, consider using larger wordlists like:
- RockYou.txt
- SecLists
- CrackStation wordlists

## Security Notes

⚠️ **Educational Purpose Only**: This tool is designed for educational and security testing purposes only.

⚠️ **Legal Compliance**: Ensure you have proper authorization before testing any systems.

⚠️ **Ethical Use**: Use responsibly and only on systems you own or have explicit permission to test.

## File Structure

```
.
├── dictionary_attack_app.py  # Main application
├── requirements.txt          # Python dependencies
├── sample_dictionary.txt    # Test wordlist
└── README.md                # This file
```

## Dependencies

- `streamlit`: Web application framework
- `pandas`: Data analysis and export functionality
- `hashlib`: Cryptographic hash functions
- `re`: Regular expressions for pattern matching

## Contributing

Feel free to submit issues and enhancement requests!
