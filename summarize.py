import nltk
import os
from pathlib import Path

# Ensure core NLTK resources are available (quiet on first run)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# function to open and read entire file as string.
def read_document(file_path):
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    elif file_ext == '.pdf':
        # Try pypdf (pure Python). If not available, fall back to PyMuPDF (fitz).
        # pypdf is preferred because it's lightweight and commonly installed as "pypdf".
        try:
            try:
                from pypdf import PdfReader
            except Exception:
                # older package name fallback
                from PyPDF2 import PdfReader

            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return '\n'.join(text_parts)
        except Exception:
            # fallback to PyMuPDF if installed
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text_parts = []
                for page in doc:
                    page_text = page.get_text("text")
                    if page_text:
                        text_parts.append(page_text)
                doc.close()
                return '\n'.join(text_parts)
            except ImportError:
                print("PyPDF reader not available. Install 'pypdf' or 'PyMuPDF' (pip install pypdf PyMuPDF)")
                return ""
            except Exception as e:
                print(f"Error reading PDF: {e}")
                return ""
    
    elif file_ext == '.docx':
        try:
            from docx import Document
            doc = Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text)
        except ImportError:
            print("python-docx is not installed. Please install it with: pip install python-docx")
            return ""
    
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: .txt, .pdf, .docx")

# process the text
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
import string

def process_text(text):
    stop_words = set(stopwords.words('english'))
    sentences = sent_tokenize(text) # split text into sentences
    word_freq = defaultdict(int)

    for sentence in sentences:
        words = word_tokenize(sentence) # split sentence into words
        for word in words:
            word = word.lower()
            # ignore stopwords and punctuation to focus on meaningful words
            if word not in stop_words and word not in string.punctuation:
                word_freq[word] += 1 # how often each word appears in the text
    return sentences, word_freq

# score sentences based on word frequencies
import heapq
def summarize(sentences, word_freq, num_sentences=5):
    sentence_scores = {} 
    for sentence in sentences:
        score=0
        words=word_tokenize(sentence.lower())
        for word in words:
            if word in word_freq:
                score += word_freq[word] # score of a sentence is the sum of frequencies of its words
        sentence_scores[sentence] = score
    # pick the highest scoring sentences to form the summary
    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    return ' '.join(summary_sentences) # join the selected sentences to form the summary

if __name__ == "__main__":
    file_path = input("Enter file path (.pdf / .docx / .txt): ").strip() 

    try:
        text = read_document(file_path)
        print(f"File processed: {file_path}")
        print(f"Extracted characters: {len(text):,}")
        if len(text.strip()) == 0:
            print("WARNING: No meaningful text extracted.")
            print("   → PDF might be scanned (image-only), protected, or have no text layer.")
            print("   → Try opening in browser and check if you can select/copy text.")
        else:
            print("First 400 characters (preview):\n")
            print(text[:400])
            print("\n" + "-"*80)

            sentences, word_freq = process_text(text)
            print(f"Sentences detected: {len(sentences)}")

            if len(sentences) > 0:
                summary = summarize(sentences, word_freq, num_sentences=5)
                print("\nSummary (top 5 sentences):")
                print(summary)
            else:
                print("No sentences found — text may be too short/jumbled.")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found. Check path & name.")
    except ImportError as ie:
        print(f"Missing library: {ie}")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")