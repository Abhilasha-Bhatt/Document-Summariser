# Document Summarizer

Simple extractive summarizer with a Streamlit UI.


[Click here to view](https://document-summary3.streamlit.app/)


Setup

1. Create and activate a venv (recommended).

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Run the UI

```bash
streamlit run app.py
```

Notes

- Supported file types: `.txt`, `.pdf`, `.docx`.
- If PDFs are image-only (scanned), the app cannot extract text without OCR.
- NLTK resources (`punkt` and `stopwords`) are downloaded automatically the first time the module is imported.

