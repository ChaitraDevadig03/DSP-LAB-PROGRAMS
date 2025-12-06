import streamlit as st
import os
from pathlib import Path
import tempfile
import json
import pandas as pd

# Import the scanner code (reuse from vuln_scanner.py)
from typing import List, Dict, Any, Optional
import re

# -------------------------
# Minimal embedded Rule + Scanner from vuln_scanner.py
# -------------------------
class Severity:
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Rule:
    def __init__(self, id, name, description, pattern, severity, languages=None, recommended_fix=""):
        self.id = id
        self.name = name
        self.description = description
        self.pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self.severity = severity
        self.languages = languages or []
        self.recommended_fix = recommended_fix

    def matches(self, text: str):
        return list(self.pattern.finditer(text))

class VulnerabilityScanner:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def scan_file(self, path: Path, language: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        lines = text.splitlines()

        for rule in self.rules:
            for m in rule.matches(text):
                line_no = text.count("\n", 0, m.start()) + 1
                snippet = lines[line_no-1] if 0 <= line_no-1 < len(lines) else ""
                results.append({
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "description": rule.description,
                    "file": str(path),
                    "line": line_no,
                    "match": m.group(0),
                    "snippet": snippet.strip(),
                    "severity": rule.severity,
                    "recommended_fix": rule.recommended_fix
                })
        return results

    def scan_path(self, root: Path) -> List[Dict[str, Any]]:
        findings = []
        for dirpath, _, filenames in os.walk(root):
            for fname in filenames:
                path = Path(dirpath) / fname
                if path.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll"]:
                    continue
                findings.extend(self.scan_file(path))
        return findings

# -------------------------
# Built-in rules (small set for demo)
# -------------------------
def built_in_rules():
    return [
        Rule("R001", "Use of eval/exec",
             "Using eval/exec is dangerous.",
             r"\b(eval|exec)\(", Severity.HIGH, ["py"],
             "Avoid eval/exec. Use safer alternatives."),
        Rule("R002", "Hardcoded secrets",
             "Possible hardcoded secret in code.",
             r"(api[_-]?key|password|secret)\s*=\s*['\"].+['\"]",
             Severity.CRITICAL, [],
             "Use environment variables or secret stores."),
        Rule("R003", "Weak hash algorithm",
             "MD5/SHA1 are weak.",
             r"\b(md5|sha1)\(", Severity.HIGH, [],
             "Use bcrypt, scrypt, Argon2, or SHA-256."),
    ]

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Vulnerability Analyzer", layout="wide")

st.title("🔍 Vulnerability Analyzer Tool")
st.write("Upload source code files or a zip folder to scan for common security vulnerabilities.")

scanner = VulnerabilityScanner(built_in_rules())

uploaded_files = st.file_uploader("Upload source code files", type=None, accept_multiple_files=True)

if uploaded_files:
    with tempfile.TemporaryDirectory() as tmpdir:
        findings = []
        for f in uploaded_files:
            path = Path(tmpdir) / f.name
            path.write_bytes(f.read())
            findings.extend(scanner.scan_file(path))

        if findings:
            st.success(f"Found {len(findings)} potential issues.")
            df = pd.DataFrame(findings)
            # Show filterable/severity-highlighted table
            st.dataframe(df[["severity", "line", "rule_name", "snippet", "recommended_fix"]])
            # Download findings
            st.download_button("Download JSON Report",
                               data=json.dumps(findings, indent=2),
                               file_name="findings.json",
                               mime="application/json")
        else:
            st.info("No issues found.")
