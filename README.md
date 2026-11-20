# 🛠️ Hinglish Complaint Router (M1)

An AI-powered campus & hostel maintenance ticket router that understands **English, Hinglish, romanised Punjabi, and regional Indian code-mixed complaints**, extracts structured metadata (`block`, `floor`, `room`, `urgency`), and routes ambiguous or multi-department tickets safely to **Human Review**.

## ✨ Key Features
- **Multilingual & Code-Mixed Understanding:** Handles messy student slang, typos, Hinglish, Punjabi, and South Indian code-mixed phrasing without rigid keyword rules.
- **Structured Metadata Extraction:** Automatically extracts `department`, `block`, `floor`, `room`, `urgency` (`low` / `medium` / `high`), `confidence`, and a plain-English `reason`.
- **Smart Human-in-the-Loop Triage:** Automatically routes vague, gibberish, or multi-department complaints (`confidence < 0.70`) to the **Human Review Queue** instead of guessing wrong.
- **Model Fallback Resilience:** Uses `gemini-3.1-flash-lite` with automatic fallback to `gemini-3.5-flash` and `gemini-3.7-flash` on rate limits or transient outages.

## 📊 Benchmark Results (`evaluate.py` — 55 Campus Test Cases)
- **Overall Routing Accuracy:** ~98% (across 6 departments + Human Review edge cases)
- **Human Review Catch Rate:** 100% (8/8 multi-issue & ambiguous traps caught)
- **Average Latency:** ~2.5 – 3.5 seconds per ticket
- **Estimated Cost:** ~$0.00039 per complaint

## 🚀 How to Run Locally
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd complaint-router
   ```
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Set your Gemini API key:
   - **Windows PowerShell:** `$env:GEMINI_API_KEY="your-api-key"`
   - **Mac/Linux:** `export GEMINI_API_KEY="your-api-key"`
4. Run the evaluation benchmark:
   ```bash
   python evaluate.py
   ```
5. Launch the interactive web app:
   ```bash
   python -m streamlit run app.py
   ```
