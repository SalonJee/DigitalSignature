# Digital Signature Simulator

This project is an interactive Streamlit application for demonstrating digital signature concepts using RSA and ElGamal schemes. It is designed as a companion tool for the presentation and report in this folder.

## What is included

- A Streamlit-based simulator for RSA signatures
- A Streamlit-based simulator for ElGamal signatures
- A theory cheat-sheet section
- A LaTeX presentation file and an HTML demo

## Project files

- [signature_simulator.py](signature_simulator.py) — main app
- [requirement.txt](requirement.txt) — dependencies list
- [digital_signatures_presentation.tex](digital_signatures_presentation.tex) — LaTeX presentation source
- [rsa_signature_demo.html](rsa_signature_demo.html) — simple HTML demo

## Requirements

This project uses Python 3 and the following packages:

- streamlit
- matplotlib
- numpy
- pandas

## Setup

1. Open the project folder.
2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:

```bash
pip install -r requirement.txt
```

If the requirements file is empty, install the packages manually:

```bash
pip install streamlit matplotlib numpy pandas
```

## Run the app

Start the simulator with:

```bash
streamlit run signature_simulator.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## How to use it

### RSA signatures

- Choose two primes `p` and `q`
- Generate RSA keys
- Sign a message
- Verify the signature
- Test tampering by changing the message and re-checking verification

### ElGamal signatures

- Generate ElGamal keys
- Sign a message
- Verify the signature
- Explore how the signature changes with different values

## Notes

- The app is meant for educational and demonstration purposes.
- If you want to share the project with others, it is best to keep the dependency list updated in [requirement.txt](requirement.txt).
