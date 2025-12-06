# TODO List for Streamlit PII Anonymization App

- [x] Create requirements.txt with dependencies: streamlit, pandas, numpy
- [x] Create app.py with Streamlit code:
  - [x] Add file uploader for CSV
  - [x] Add option to use sample data
  - [x] Display uploaded or sample data
  - [x] Implement data classification (structured/unstructured, states: in-transit/at-rest/in-use)
  - [x] Highlight PII elements (identify columns containing PII)
  - [x] Allow selection of quasi-identifiers and k value for anonymization
  - [x] Implement k-anonymity anonymization (generalize quasi-identifiers)
  - [x] Evaluate and display re-identification risk before and after anonymization
- [x] Ensure app is runnable with `streamlit run app.py`
- [x] Install dependencies using pip install -r requirements.txt
- [x] Run the app to test functionalities
- [x] Verify all features work as expected
