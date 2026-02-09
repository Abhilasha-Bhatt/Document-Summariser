import nltk
import os
from pathlib import Path
from docx import Document
from pypdf import PdfReader
import streamlit as st
import tempfile

# Import core summarizer functions from the library file
from summarize import read_document, process_text, summarize

nltk.download('punkt_tab', quiet=True) # for sentence tokenization
nltk.download('stopwords', quiet=True) # for stopword removal

# Configure Streamlit page
st.set_page_config(page_title="Document Summarizer", layout="wide")

def main():
    st.title("Document Summarizer")
    st.markdown("Upload a `.txt`, `.pdf` or `.docx` file and get a quick extractive summary.")

    uploaded_file = st.file_uploader("Choose a document", type=["txt", "pdf", "docx"])

    num_sentences = st.sidebar.slider("Number of sentences", 3, 15, 5)

    if uploaded_file is not None:
        st.success(f"Uploaded: {uploaded_file.name}")

        # write uploaded bytes to a temp file so existing read_document(file_path) can be reused
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            with st.spinner("Extracting text..."):
                text = read_document(tmp_path)

            if not text or not text.strip():
                st.error("No extractable text found. The file may be image-only (scanned) or empty.")
            else:
                st.success(f"Extracted {len(text):,} characters")

                with st.expander("Preview document (first 1000 chars)"):
                    st.text(text[:1000] + ("..." if len(text) > 1000 else ""))

                with st.spinner("Scoring and summarizing..."):
                    sentences, word_freq = process_text(text)
                    if not sentences:
                        st.warning("No sentences detected — nothing to summarize.")
                    else:
                        summary = summarize(sentences, word_freq, num_sentences=num_sentences)
                        st.header("Summary")
                        st.write(summary)

                        st.info(f"Original ≈ {len(text.split()):,} words — Summary ≈ {len(summary.split()):,} words")

        except Exception as e:
            st.error(f"Error processing file: {e}")
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

if __name__ == "__main__":
    main()